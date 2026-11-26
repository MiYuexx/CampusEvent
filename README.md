# CampusEvent 校园活动报名与管理系统（实验二）

基于设计模式的校园活动报名与管理系统，项目代号 CampusEvent。后端使用 Python + Flask，数据库使用 SQLite；报名规则采用策略模式，报名业务与站内通知通过观察者/事件分发机制解耦。

## 一、环境依赖

- Python 3.11 及以上
- 依赖清单见 `requirements.txt`

## 二、从零开始运行

```bash
# 1. 进入项目目录
cd CampusEvent

# 2.（可选）创建虚拟环境
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
flask --app app run --host 0.0.0.0 --port 5000
```

浏览器访问：

- 本机调试：`http://127.0.0.1:5000`
- 公网部署地址：见下方「部署说明」，必须使用可被公网访问的地址，不能填写本机回环地址。

## 三、运行测试

```bash
python -m pytest tests/ -q
```

测试覆盖指导书 3.5 节 C1–C10 全部初始版本验收用例。

## 四、功能清单

| 编号 | 功能 | 说明 |
| --- | --- | --- |
| P2-F01 | 活动管理 | 管理员创建活动，设置名称、类别、地点、人数上限、报名方式 |
| P2-F02 | 活动查看 | 浏览活动列表，可按名称筛选 |
| P2-F03 | 报名/取消 | 学生报名、取消；禁止同一活动出现重复有效报名 |
| P2-F04 | 报名策略 | 直接报名自动通过；审核型报名进入待审核 |
| P2-F05 | 审批操作 | 管理员批准/拒绝待审核申请，批准时再次检查名额 |
| P2-F06 | 状态管理 | 待审核、已通过、已拒绝、已取消，状态转换符合规则 |
| P2-F07 | 站内通知 | 报名结果与审核结果写入站内消息列表 |
| P2-F08 | 统计 | 按活动查看已通过数、待审核数和剩余名额 |

## 五、目录结构

```
CampusEvent/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── database.py          # SQLite 连接与建表
│   ├── routes.py            # HTTP 接口与页面路由
│   ├── service.py           # 报名业务服务
│   ├── policies/            # 策略模式：报名规则抽象与实现
│   └── observers/           # 观察者模式：事件分发与站内消息
├── tests/                   # pytest 验收用例 C1–C10
├── docs/                    # SRS 分析、设计文档、测试记录、变更分析
├── templates/               # 前端页面
├── AI_DEV_LOG.md            # AI 协作过程记录
├── requirements.txt
└── README.md
```

## 六、部署说明（公网 Web 地址）

本项目为 Flask 后端应用，公网部署可任选其一：

1. 云服务器：将代码上传至云服务器，安装依赖后用 gunicorn/uwsgi 配合 Nginx 对外提供服务，Web 地址形如 `http://<服务器公网IP>:5000` 或绑定域名。
2. 平台托管：使用支持 Python 后端的 PaaS（如 Render、Railway、阿里云/腾讯云应用托管等），连接本仓库后按 `requirements.txt` 安装依赖、启动命令 `flask --app app run --host 0.0.0.0 --port $PORT`。

> 提交作业时，在答案中填写：
>
> - 代码仓库：`<GitHub 仓库地址>`
> - 项目 Web 地址：`<公网可访问地址>`

## 七、Git 版本标签

- `baseline-v1`：初始验收版本，对应 C1–C10 全部通过。
- `change-v2`：需求变更完成版本（变更单发布后在 `baseline-v1` 基础上创建分支实现，详见 `docs/change-analysis.md`）。
