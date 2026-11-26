from .base import RegistrationPolicy


class GradeDirectPolicy(RegistrationPolicy):
    """CR-01 年级限定直接报名：仅大二、大三学生可报，名额充足自动通过。"""

    code = "GRADE_DIRECT"
    ALLOWED_GRADES = (2, 3)

    def initial_status(self, activity, approved_count, student=None):
        grade = None if student is None else student.get("grade")
        if grade not in self.ALLOWED_GRADES:
            raise ValueError("该活动仅面向大二、大三学生，当前年级不可报名")
        if approved_count >= activity["capacity"]:
            raise ValueError("名额不足")
        return "APPROVED"

    def can_approve(self, activity, approved_count, student=None):
        return approved_count < activity["capacity"]
