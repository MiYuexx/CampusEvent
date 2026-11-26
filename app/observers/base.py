from abc import ABC, abstractmethod


class EventObserver(ABC):
    @abstractmethod
    def on_event(self, event_type, payload):
        """接收报名/审批事件；通知失败不得反向回滚已合法提交的报名。"""
