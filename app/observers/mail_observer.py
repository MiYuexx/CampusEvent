from ..database import get_db
from .base import EventObserver


class MailObserver(EventObserver):
    """CR-02 邮件订阅者：报名/审批事件在站内通知之外同步发模拟邮件。

    - 邮件失败写入 mail_log 留痕，不向业务流程抛出，避免回滚已提交报名。
    - 同一学生、活动、主题、内容只记录一次，防止重复发送。
    """

    def __init__(self, mail_sender):
        self.mail_sender = mail_sender

    def on_event(self, event_type, payload):
        db = get_db()
        student_id = payload["student_id"]
        activity_id = payload["activity_id"]
        content = payload["content"]
        subject = f"[CampusEvent] 活动报名通知"

        duplicate = db.execute(
            "SELECT 1 FROM mail_log WHERE student_id = ? AND activity_id = ? AND subject = ? AND content = ?",
            (student_id, activity_id, subject, content),
        ).fetchone()
        if duplicate:
            return

        try:
            self.mail_sender.send(to=student_id, subject=subject, content=content)
            db.execute(
                "INSERT INTO mail_log (student_id, activity_id, subject, content, status, error) VALUES (?, ?, ?, ?, 'SENT', NULL)",
                (student_id, activity_id, subject, content),
            )
        except Exception as exc:
            db.execute(
                "INSERT INTO mail_log (student_id, activity_id, subject, content, status, error) VALUES (?, ?, ?, ?, 'FAILED', ?)",
                (student_id, activity_id, subject, content, str(exc)),
            )
        db.commit()
