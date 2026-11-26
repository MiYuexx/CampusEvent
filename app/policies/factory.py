from .direct import DirectPolicy
from .review import ReviewPolicy
from .grade_direct import GradeDirectPolicy

_POLICIES = {
    DirectPolicy.code: DirectPolicy(),
    ReviewPolicy.code: ReviewPolicy(),
    GradeDirectPolicy.code: GradeDirectPolicy(),
}


def get_policy(policy_type):
    if policy_type not in _POLICIES:
        raise ValueError("未知报名方式")
    return _POLICIES[policy_type]
