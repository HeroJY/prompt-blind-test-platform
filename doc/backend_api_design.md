# Prompt盲选测试平台后端设计文档

## 1. 文档说明

本文档基于当前仓库中的实际代码整理，目标是准确描述当前后端实现，而不是描述理想规划版本。

当前代码目录：

```text
prompt-blind-test-platform/
├── web/         # 前端
└── python-app/  # 后端
```

其中：

1. 前端路径为 `prompt-blind-test-platform/web`
2. 后端路径为 `prompt-blind-test-platform/python-app`
3. 当前最稳定的后端运行入口是 `python-app/simple_server.py`

---

## 2. 当前系统边界

### 2.1 登录与认证

当前系统保留“伪登录”，不做真实认证。

实际行为：

1. 前端登录页只负责角色切换与进入系统
2. 用户名和密码不会提交到后端校验
3. 后端没有 `/auth/login`、JWT、Session、Cookie 等认证机制
4. 所有业务接口都通过请求体中的 `operator` 标识当前操作者

统一结构：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  }
}
```

说明：

1. `operator` 当前只用于记录创建人和做最基础的角色判断
2. 如果后续要升级为正式系统，可以在保留业务接口不变的前提下增加认证层

### 2.2 接口设计风格

当前所有业务接口统一使用 `POST`。

统一前缀：

`/api/v1`

统一响应格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误示例：

```json
{
  "code": 4004,
  "message": "task not found",
  "data": null
}
```

### 2.3 运行环境

当前运行目标是 Python 3.6.10。

代码中保留了两套入口：

1. `simple_server.py`
   使用 Python 标准库实现，可直接运行
2. `app/main.py`
   保留 FastAPI 风格入口，便于后续升级

当前推荐运行方式：

```bash
/Users/shala/opt/anaconda3/envs/python36/bin/python simple_server.py
```

---

## 3. 当前后端目录结构

```text
python-app/
├── README.md
├── requirements.txt
├── simple_server.py
├── smoke_test.py
├── app/
│   ├── main.py
│   ├── config.py
│   ├── core/
│   ├── api/
│   └── services/
└── data/
    ├── tasks.json
    └── sessions.json
```

说明：

1. `simple_server.py` 是当前实际联调使用的入口
2. `app/services/` 中保存任务、会话、存储、Excel 解析等核心逻辑
3. `data/tasks.json` 与 `data/sessions.json` 是当前真实数据源

---

## 4. 核心数据模型

### 4.1 Operator

```json
{
  "username": "admin01",
  "role": "admin"
}
```

### 4.2 Task

当前任务对象使用 camelCase 字段，真实结构如下：

```json
{
  "id": 1,
  "name": "客服回复质量对比（V3 vs V4）",
  "description": "比较两组提示词在客服安抚回复中的可读性、同理心表达、规则解释与补偿建议完整度。",
  "promptA": "你是一名资深客服专家，请输出安抚式回复......",
  "promptB": "请作为高情商客服生成回复......",
  "promptAImages": [
    {
      "name": "prompt-a-1.png",
      "type": "image/png",
      "url": "/uploads/prompts/task_1/prompt_a/abc123.png"
    }
  ],
  "promptBImages": [],
  "testData": "order_id=123456\nproduct_name=手机壳",
  "status": "published",
  "visibility": "public",
  "questionLimit": 49,
  "createdBy": "admin01",
  "createdAt": "2026-04-19T10:00:00+08:00",
  "updatedAt": "2026-04-19T10:00:00+08:00",
  "items": []
}
```

字段说明：

1. `promptA`、`promptB` 是文字 Prompt
2. `promptAImages`、`promptBImages` 是 Prompt 图片
3. Prompt 图片当前实际保存为本地文件，`tasks.json` 中只保留图片元数据与访问 URL
4. `visibility` 当前支持 `public` 和 `private`
5. `status` 当前主要使用 `draft` 和 `published`

### 4.3 TaskItem

```json
{
  "id": 101,
  "code": "Q001",
  "sourceType": "text",
  "sortOrder": 1,
  "sourceText": "用户投诉昨天买的商品今天降价了......",
  "images": []
}
```

说明：

1. 当前题目以文本题为主
2. `images` 字段已保留，但当前批量导入不开放图片题

### 4.4 Session

```json
{
  "id": "s_1776617768207",
  "taskId": 1,
  "userId": "tester01",
  "status": "in_progress",
  "answeredCount": 0,
  "answers": [],
  "userInputs": {},
  "testDataByQuestion": {},
  "questions": [],
  "startTime": "2026-04-20T10:00:00",
  "endTime": null
}
```

### 4.5 Session Question

每道题的生成结果、投票结果、裁判结果都保存在 `session.questions` 中：

```json
{
  "id": 101,
  "code": "Q001",
  "sourceType": "text",
  "sortOrder": 1,
  "sourceText": "请生成客服安抚回复",
  "images": [],
  "answerA": "......",
  "answerB": "......",
  "questionRecordId": "sq_s_1776617768207_1",
  "promptMapping": {
    "a": "prompt_a",
    "b": "prompt_b"
  },
  "modelJudge": {
    "recommended": "A",
    "reason": "......"
  },
  "testData": "order_id=9988"
}
```

关键约束：

1. 前端只看到候选回答 A / B
2. A/B 与真实 Prompt A/B 的映射只保存在后端
3. 统计结果必须按 `selectedPrompt` 做真实归因

---

## 5. Prompt、上传与导入策略

### 5.1 Prompt 配置方式

当前前端主流程中，Prompt 配置方式已经不是 Excel 导入，而是：

1. 手动输入 Prompt A 文字
2. 手动输入 Prompt B 文字
3. 分别上传 Prompt A / Prompt B 图片

当前 Prompt 的能力边界：

1. 图片 Prompt 可以保存与展示
2. 图片 Prompt 当前不会被真正解析为多模态输入
3. 如果 Prompt 只有图片、没有文字，后端生成逻辑会使用“图像提示词，共 N 张”作为兜底说明
4. Prompt 图片会写入本地目录 `python-app/data/uploads/prompts/`

### 5.2 Excel 上传策略

当前正式开放的 Excel 上传能力有两类：

1. `POST /api/v1/upload/item_excel`
2. `POST /api/v1/upload/test_data_excel`

规则：

1. 当前只支持 `.xlsx`
2. `.xls` 暂不支持
3. ZIP 路由保留但不开放

### 5.3 题目 Excel 模板

推荐字段：

| code | sort_order | source_type | source_text |
| ---- | ---- | ---- | ---- |
| Q001 | 1 | text | 用户投诉昨天买的商品今天降价了 |
| Q002 | 2 | text | 用户反馈快递延迟两天 |

说明：

1. 当前只建议使用 `source_type=text`
2. 图片题批量导入暂不开放

### 5.4 测试数据 Excel 模板

推荐字段：

| data_key | data_value |
| ---- | ---- |
| order_id | 123456 |
| product_name | 手机壳 |
| complaint_reason | 昨天下单今天降价 |

---

## 6. 当前已实现接口

### 6.1 系统接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/system/ping` | 服务探活 |

### 6.2 任务接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/task/list` | 获取任务列表 |
| POST | `/api/v1/task/create` | 创建任务 |
| POST | `/api/v1/task/detail` | 获取任务详情 |
| POST | `/api/v1/task/update` | 更新任务 |
| POST | `/api/v1/task/delete` | 删除任务 |
| POST | `/api/v1/task/publish` | 发布任务 |

### 6.3 题目接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/task/item/list` | 获取题目列表 |
| POST | `/api/v1/task/item/create` | 新增单题 |
| POST | `/api/v1/task/item/delete` | 删除单题 |
| POST | `/api/v1/task/item/import_excel` | 通过结构化数据导入题目 |

说明：

1. `task/item/update` 当前没有实现
2. 前端当前也没有逐题编辑题目的流程

### 6.4 上传接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/upload/item_excel` | 上传题目 Excel |
| POST | `/api/v1/upload/test_data_excel` | 上传测试数据 Excel |
| POST | `/api/v1/upload/task_zip` | 预留 ZIP 上传接口，当前返回未开放 |

### 6.5 会话接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/session/start` | 开始测试 |
| POST | `/api/v1/session/detail` | 获取会话详情 |
| POST | `/api/v1/session/generate` | 生成候选回答 |
| POST | `/api/v1/session/vote` | 保存投票 |
| POST | `/api/v1/session/judge` | 大模型裁判 |
| POST | `/api/v1/session/finish` | 正常结束测试 |
| POST | `/api/v1/session/quit` | 中途退出测试 |

### 6.6 历史接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/history/task_list` | 获取任务历史记录 |
| POST | `/api/v1/history/session_detail` | 获取单次测试详情 |
| POST | `/api/v1/history/question/delete` | 删除某条历史题目记录 |

### 6.7 统计接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/stats/task_overview` | 获取任务整体统计 |
| POST | `/api/v1/stats/task_items` | 获取分题统计 |
| POST | `/api/v1/stats/dashboard_overview` | 获取后台概览统计 |

### 6.8 AI 接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/ai/prompt_generate` | 一键生成 Prompt |

---

## 7. 重点接口说明

### 7.1 获取任务列表

`POST /api/v1/task/list`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  }
}
```

当前行为：

1. 测试用户可以看到已发布任务
2. 测试用户也可以看到自己创建的私有任务
3. 管理员可以看到全部任务
4. 当前没有实现复杂筛选条件

### 7.2 创建任务

`POST /api/v1/task/create`

请求示例：

```json
{
  "operator": {
    "username": "admin01",
    "role": "admin"
  },
  "task": {
    "name": "客服回复质量对比",
    "description": "比较两组提示词效果",
    "visibility": "public",
    "questionLimit": 49,
    "promptA": "......",
    "promptB": "......",
    "promptAImages": [],
    "promptBImages": [],
    "testData": ""
  }
}
```

说明：

1. Prompt A / B 可以只填文字
2. Prompt A / B 也可以只上传图片
3. 当前前端发布前会要求 Prompt A / B 至少各有一种内容

### 7.3 开始测试

`POST /api/v1/session/start`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "taskId": 1,
  "questionLimit": 49
}
```

说明：

1. 当前会话会按 `questionLimit` 初始化题目槽位
2. 如果任务题目数不足，会自动补空白题槽

### 7.4 生成候选回答

`POST /api/v1/session/generate`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "sessionId": "s_1776617768207",
  "slotIndex": 0,
  "originalQuestion": "请生成客服安抚回复",
  "testData": "订单号123，用户反馈降价"
}
```

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "questionRecordId": "sq_s_1776617768207_1",
    "candidateA": "您好，很抱歉给您带来不好的体验......",
    "candidateB": "非常抱歉让您遇到这样的情况......"
  }
}
```

当前行为：

1. 后端内部随机决定候选回答 A / B 与真实 Prompt A / B 的映射关系
2. 前端不会拿到真实映射
3. 当前生成逻辑是本地 mock，不是真实模型调用
4. 当前模型裁判也是本地 mock

### 7.5 保存投票

`POST /api/v1/session/vote`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "sessionId": "s_1776617768207",
  "questionRecordId": "sq_s_1776617768207_1",
  "selectedOption": "A"
}
```

行为要求：

1. 同一题重复投票以后一次为准
2. 保存时同时记录用户选择的 `selectedOption`
3. 后端同时保存真实归因字段 `selectedPrompt`

---

## 8. 文件存储设计

当前真实结构：

```text
data/
├── tasks.json
├── sessions.json
└── uploads/
```

当前实现说明：

1. `tasks.json` 保存任务主信息、Prompt 文字、Prompt 图片、题目列表
2. `sessions.json` 保存会话、作答、裁判结果与真实 Prompt 映射
3. `uploads/` 目录当前用于保存 Prompt 图片本地文件

当前方案优点：

1. 简单
2. 适合本地原型联调
3. 搬迁项目时只需要带走源码和 JSON 文件

当前方案限制：

1. Prompt 图片实际保存在本地目录 `data/uploads/prompts/`
2. `tasks.json` 中保存的是图片元数据和 `/uploads/...` 访问路径
3. Prompt 图片不走 JSON 内嵌存储，只能走本地文件路径
4. 后续正式化时建议拆为对象存储或独立文件服务

---

## 9. 当前前后端分工

### 9.1 已显式走后端的主流程

1. 任务列表加载
2. 任务创建、保存、发布、删除
3. 单题新增、删除
4. 题目 Excel 导入
5. 测试数据 Excel 导入
6. 开始测试、生成回答、投票、裁判、结束测试
7. 历史记录删除
8. 任务统计与分题统计
9. Prompt 一键生成

### 9.2 仍保留前端本地处理的部分

1. 伪登录
2. 页面导航与返回
3. 临时任务草稿态
4. Prompt 图片的本地读取与预览

---

## 10. 当前实现注意点

1. 当前不是生产级认证方案
2. 当前所有接口都使用 camelCase 字段
3. 批量导入题目仍然只支持 `.xlsx`
4. Prompt 主流程已经改为“文字 + 图片”，不再依赖 Prompt Excel
5. Prompt 图片只允许保存到本地目录，不做 dataUrl 持久化兼容
6. ZIP 路由保留，但必须返回“未开放”
7. Prompt 图片当前只做保存与展示，不参与真实多模态推理
8. Python 3.6 下不要使用 `list[str]`、`|` 联合类型、`match-case` 等新语法
