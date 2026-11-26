from datetime import datetime

from .database import get_db
from .policies.factory import get_policy
from .observers.dispatcher import EventDispatcher
from .observers.message_observer import MessageObserver
from .observers.mail_sender import MockEmailSender
from .observers.mail_observer import MailObserver

VALID_STATUS = {"PENDING", "APPROVED", "REJECTED", "CANCELLED"}
ACTIVE_STATUS = {"PENDING", "APPROVED"}
VALID_POLICIES = ("DIRECT", "REVIEW", "GRADE_DIRECT")


class RegistrationService:
    def __init__(self, mail_sender=None):
        self.dispatcher = EventDispatcher()
        self.mail_sender = mail_sender or MockEmailSender()
        self.mail_observer = MailObserver(self.mail_sender)
        self.dispatcher.subscribe(MessageObserver())
        self.dispatcher.subscribe(self.mail_observer)

    def set_mail_sender(self, mail_sender):
        self.mail_sender = mail_sender
        self.mail_observer.mail_sender = mail_sender

    # ---------- 活动管理 ----------
    def create_activity(self, title, category, start_at, location, capacity, policy_type):
        if not title or not title.strip():
            raise ValueError("活动名称不能为空")
        capacity = int(capacity)
        if capacity <= 0:
            raise ValueError("人数上限必须为正整数")
        if policy_type not in VALID_POLICIES:
            raise ValueError("报名方式无效")
        db = get_db()
        cur = db.execute(
            "INSERT INTO activity (title, category, start_at, location, capacity, policy_type) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title.strip(), category, start_at, location, capacity, policy_type),
        )
        db.commit()
        return cur.lastrowid

    def list_activities(self, keyword=None):
        db = get_db()
        sql = "SELECT * FROM activity"
        params = []
        if keyword:
            sql += " WHERE title LIKE ?"
            params.append(f"%{keyword}%")
        sql += " ORDER BY activity_id DESC"
        rows = db.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_activity(self, activity_id):
        row = get_db().execute("SELECT * FROM activity WHERE activity_id = ?", (activity_id,)).fetchone()
        return dict(row) if row else None

    def _get_student(self, db, student_id):
        row = db.execute("SELECT * FROM student WHERE student_id = ?", (student_id,)).fetchone()
        return dict(row) if row else None

    # ---------- 报名 ----------
    def _approved_count(self, db, activity_id):
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM registration WHERE activity_id = ? AND status = 'APPROVED'",
            (activity_id,),
        ).fetchone()
        return row["cnt"]

    def _has_active_registration(self, db, activity_id, student_id):
        row = db.execute(
            "SELECT 1 FROM registration WHERE activity_id = ? AND student_id = ? AND status IN ('PENDING', 'APPROVED')",
            (activity_id, student_id),
        ).fetchone()
        return row is not None

    def register(self, activity_id, student_id, student_name=None, grade=None):
        db = get_db()
        activity = self.get_activity(activity_id)
        if not activity:
            raise ValueError("活动不存在")

        if self._has_active_registration(db, activity_id, student_id):
            raise ValueError("该活动已有有效报名，请勿重复报名")

        student = self._get_student(db, student_id)
        if student is None:
            if grade is not None and not (1 <= int(grade) <= 4):
                raise ValueError("年级必须为 1—4")
            db.execute(
                "INSERT OR IGNORE INTO student (student_id, name, grade) VALUES (?, ?, ?)",
                (student_id, student_name or student_id, grade),
            )
            student = self._get_student(db, student_id)
        elif grade is not None:
            db.execute("UPDATE student SET grade = ? WHERE student_id = ?", (grade, student_id))
            student["grade"] = grade

        policy = get_policy(activity["policy_type"])
        approved_count = self._approved_count(db, activity_id)
        status = policy.initial_status(activity, approved_count, student)

        cur = db.execute(
            "INSERT INTO registration (activity_id, student_id, status) VALUES (?, ?, ?)",
            (activity_id, student_id, status),
        )
        db.commit()

        if status == "APPROVED":
            content = f"你报名的活动《{activity['title']}》已通过。"
        else:
            content = f"你报名的活动《{activity['title']}》已提交，等待管理员审核。"
        self.dispatcher.publish(
            "REGISTERED",
            {"student_id": student_id, "activity_id": activity_id, "content": content},
        )
        return cur.lastrowid, status

    def review(self, registration_id, approve):
        db = get_db()
        row = db.execute("SELECT * FROM registration WHERE registration_id = ?", (registration_id,)).fetchone()
        if not row:
            raise ValueError("报名记录不存在")
        if row["status"] != "PENDING":
            raise ValueError("仅待审核记录可审批")

        activity = self.get_activity(row["activity_id"])
        student = self._get_student(db, row["student_id"])
        policy = get_policy(activity["policy_type"])
        approved_count = self._approved_count(db, row["activity_id"])

        if approve and not policy.can_approve(activity, approved_count, student):
            raise ValueError("名额已满，批准失败")

        new_status = "APPROVED" if approve else "REJECTED"
        db.execute(
            "UPDATE registration SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE registration_id = ?",
            (new_status, registration_id),
        )
        db.commit()

        if approve:
            content = f"你的报名《{activity['title']}》已被管理员批准。"
        else:
            content = f"你的报名《{activity['title']}》未通过审核。"
        self.dispatcher.publish(
            "REVIEWED",
            {"student_id": row["student_id"], "activity_id": activity["activity_id"], "content": content},
        )
        return new_status

    def cancel(self, registration_id):
        db = get_db()
        row = db.execute("SELECT * FROM registration WHERE registration_id = ?", (registration_id,)).fetchone()
        if not row:
            raise ValueError("报名记录不存在")
        if row["status"] not in ("PENDING", "APPROVED"):
            raise ValueError("当前状态不可取消")
        db.execute(
            "UPDATE registration SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP WHERE registration_id = ?",
            (registration_id,),
        )
        db.commit()
        activity = self.get_activity(row["activity_id"])
        self.dispatcher.publish(
            "CANCELLED",
            {
                "student_id": row["student_id"],
                "activity_id": row["activity_id"],
                "content": f"你已取消活动《{activity['title']}》的报名。",
            },
        )
        return "CANCELLED"

    # ---------- 统计与查询 ----------
    def activity_stats(self, activity_id):
        db = get_db()
        approved = self._approved_count(db, activity_id)
        pending = db.execute(
            "SELECT COUNT(*) AS cnt FROM registration WHERE activity_id = ? AND status = 'PENDING'",
            (activity_id,),
        ).fetchone()["cnt"]
        activity = self.get_activity(activity_id)
        return {
            "activity_id": activity_id,
            "approved": approved,
            "pending": pending,
            "remaining": max(activity["capacity"] - approved, 0),
            "capacity": activity["capacity"],
        }

    def list_messages(self, student_id):
        rows = get_db().execute(
            "SELECT * FROM message WHERE student_id = ? ORDER BY message_id DESC",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_mail_logs(self, student_id=None):
        db = get_db()
        if student_id is not None:
            rows = db.execute("SELECT * FROM mail_log WHERE student_id = ? ORDER BY mail_id DESC", (student_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM mail_log ORDER BY mail_id DESC").fetchall()
        return [dict(r) for r in rows]

    def list_registrations(self, activity_id=None):
        db = get_db()
        if activity_id is not None:
            rows = db.execute("SELECT * FROM registration WHERE activity_id = ?", (activity_id,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM registration ORDER BY registration_id DESC").fetchall()
        return [dict(r) for r in rows]
