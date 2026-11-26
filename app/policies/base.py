from abc import ABC, abstractmethod


class RegistrationPolicy(ABC):
    """报名策略抽象：策略只决定初始/审批时的业务判定，公共名额与重复校验由服务层统一处理。"""

    code = ""

    @abstractmethod
    def initial_status(self, activity, approved_count):
        """提交报名时返回初始状态。"""

    @abstractmethod
    def can_approve(self, activity, approved_count):
        """审批时是否允许通过。"""
