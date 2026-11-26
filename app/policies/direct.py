from .base import RegistrationPolicy


class DirectPolicy(RegistrationPolicy):
    """直接报名：名额充足即自动通过。"""

    code = "DIRECT"

    def initial_status(self, activity, approved_count, student=None):
        if approved_count >= activity["capacity"]:
            raise ValueError("名额不足")
        return "APPROVED"

    def can_approve(self, activity, approved_count, student=None):
        return approved_count < activity["capacity"]
