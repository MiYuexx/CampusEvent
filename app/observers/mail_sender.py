import time


class MockEmailSender:
    """CR-02 模拟邮件发送器：不接真实邮件服务器，记录收件人、主题、内容、状态与时间。

    fail_next 置为 True 时，下一次发送抛出异常，用于验证邮件失败不回滚报名。
    """

    def __init__(self):
        self.sent = []
        self.fail_next = False

    def send(self, to, subject, content):
        record = {
            "to": to,
            "subject": subject,
            "content": content,
            "status": "SENT",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": None,
        }
        if self.fail_next:
            record["status"] = "FAILED"
            record["error"] = "模拟邮件服务器不可用"
            self.sent.append(record)
            raise RuntimeError(record["error"])
        self.sent.append(record)
        return record
