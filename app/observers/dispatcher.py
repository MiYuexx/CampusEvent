class EventDispatcher:
    """极简事件分发：业务流程只发布事件，通知写入由观察者完成，实现解耦。"""

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def publish(self, event_type, payload):
        for observer in self._observers:
            try:
                observer.on_event(event_type, payload)
            except Exception:
                # 通知失败留痕思路：此处不向业务流程抛出，避免通知问题导致报名事务回滚
                continue
