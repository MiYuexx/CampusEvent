# UML 类图（文本版）

> 说明：本文件为类图结构的文本描述；正式提交时可按本结构导出为图片插入实验报告。

## 类关系

```
┌─────────────────────┐
│       Student        │
├─────────────────────┤
│ - student_id: String│
│ - name: String      │
└─────────────────────┘

┌─────────────────────┐
│       Activity      │
├─────────────────────┤
│ - activity_id: int  │
│ - title: String     │
│ - category: String   │
│ - start_at: String  │
│ - location: String  │
│ - capacity: int     │
│ - policy_type: enum │
└─────────────────────┘

┌──────────────────────────┐
│      Registration        │
├──────────────────────────┤
│ - registration_id: int   │
│ - activity_id: int       │
│ - student_id: String     │
│ - status: enum           │
│ - created_at: datetime   │
│ - updated_at: datetime   │
└──────────────────────────┘

┌──────────────────────────────┐
│   <<abstract>>               │
│   RegistrationPolicy         │
├──────────────────────────────┤
│ + initial_status(...) : enum │
│ + can_approve(...) : bool    │
└──────────────────────────────┘
            ▲
            │ implements
 ┌──────────┴───────────┐
 │                      │
┌──────────────┐   ┌──────────────┐
│ DirectPolicy │   │ ReviewPolicy │
└──────────────┘   └──────────────┘

┌────────────────────────────┐
│      EventDispatcher       │
├────────────────────────────┤
│ - observers: List          │
│ + subscribe(observer)      │
│ + publish(type, payload)   │
└────────────────────────────┘
            │ 1..* 订阅
            ▼
┌────────────────────────────┐
│   <<interface>>            │
│   EventObserver            │
├────────────────────────────┤
│ + on_event(type, payload)  │
└────────────────────────────┘
            ▲
            │ implements
┌────────────────────────────┐
│    MessageObserver         │
├────────────────────────────┤
│ + on_event(type, payload)  │
└────────────────────────────┘

┌─────────────────────┐
│       Message       │
├─────────────────────┤
│ - message_id: int   │
│ - student_id: String│
│ - activity_id: int  │
│ - content: String  │
│ - is_read: bool     │
└─────────────────────┘

┌──────────────────────────────────────┐
│      RegistrationService             │
├──────────────────────────────────────┤
│ - dispatcher: EventDispatcher         │
│ + create_activity(...)                 │
│ + register(activity_id, student_id)   │
│ + review(registration_id, approve)   │
│ + cancel(registration_id)             │
│ + activity_stats(activity_id)          │
└──────────────────────────────────────┘
```

## 关联与依赖

- `Registration` 关联 `Student` 与 `Activity`（多对一）。
- `RegistrationService` 依赖 `RegistrationPolicy` 抽象与 `EventDispatcher`。
- `EventDispatcher` 依赖 `EventObserver` 接口；`MessageObserver` 写入 `Message`。
- 具体策略由工厂 `get_policy(policy_type)` 按活动报名方式创建。
