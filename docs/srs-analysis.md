# 实验二 初始需求（SRS）分析

## 1. 产品定义

系统名称：CampusEvent 校园活动报名与管理系统。

目标用户：校园管理员（Admin）与学生（Student），使用固定演示账号，不做注册与复杂权限。

运行方式：B/S 架构，浏览器访问；后端 Python + Flask，数据持久化到 SQLite。

## 2. 领域数据

| 对象 | 主要字段 | 约束 |
| --- | --- | --- |
| Student | student_id、name | 学生 ID 唯一 |
| Activity | activity_id、title、category、start_at、location、capacity、policy_type | 容量为正整数；报名方式为 DIRECT / REVIEW |
| Registration | registration_id、activity_id、student_id、status、created_at、updated_at | 状态：PENDING / APPROVED / REJECTED / CANCELLED |
| Message | message_id、student_id、activity_id、content、is_read、created_at | 报名或审核动作产生站内消息 |

## 3. 角色与用例说明

### 管理员
- 创建、编辑、删除活动，设置活动信息与报名方式。
- 对待审核报名执行批准或拒绝；批准时再次检查剩余名额。
- 查看各活动报名统计。

### 学生
- 浏览活动列表与详情，按名称筛选。
- 提交报名、取消本人报名。
- 查看与本人相关的站内通知。

## 4. 业务规则

1. 直接报名活动：名额充足时报名直接「已通过」，并产生站内通知。
2. 审核型活动：提交后为「待审核」，由管理员批准或拒绝；批准时再次检查名额。
3. 名额统计按「已通过」报名计算；待审核不占名额；满员后不得再批准新报名。
4. 同一学生对同一活动不得存在两条「待审核」或「已通过」的有效报名；已取消/已拒绝记录保留历史，允许再次申请。
5. 学生可取消本人「待审核」或「已通过」报名。
6. 通知失败只留痕，不得导致已合法提交的报名记录消失。
7. 活动与报名记录必须持久化，重启服务后数据一致。

## 5. 范围外需求

- 不实现用户注册、登录鉴权与多角色权限体系。
- 不接入邮件、短信、微信推送等第三方通知渠道。
- 不做移动端 App、复杂日历与活动推荐算法。
