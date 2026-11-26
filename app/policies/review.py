from .base import RegistrationPolicy


class ReviewPolicy(RegistrationPolicy):
    """审核型报名：先进入待审核，审批时再次检查名额。"""

    code = "REVIEW"

    def initial_status(self, activity, approved_count):
        return "PENDING"

    def can_approve(self, activity, approved_count):
        return approved_count < activity["capacity"]
