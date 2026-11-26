from ..database import get_db
from .base import EventObserver


class MessageObserver(EventObserver):
    """把报名结果、审批结果写入站内消息表。同一报名同一状态事件只写一条，避免重复通知。"""

    def on_event(self, event_type, payload):
        db = get_db()
        student_id = payload["student_id"]
        activity_id = payload["activity_id"]
        content = payload["content"]

        duplicate = db.execute(
            "SELECT 1 FROM message WHERE student_id = ? AND activity_id = ? AND content = ?",
            (student_id, activity_id, content),
        ).fetchone()
        if duplicate:
            return

        db.execute(
            "INSERT INTO message (student_id, activity_id, content) VALUES (?, ?, ?)",
            (student_id, activity_id, content),
        )
        db.commit()
