# Prompt盲选测试平台后端设计文档

## 1. 文档目标

本文档基于当前前端原型整理后端接口与代码结构，重点响应以下约束：

1. 系统仅自用，第一版不做完整认证体系
2. 所有后端接口统一设计为 `POST`
3. 文件上传当前只开放 Excel 上传
4. ZIP 导入功能只预留，不对外开放
5. 后端基于 Python 3.6 开发
6. 后端代码放到一个新的独立目录中

## 2. 当前后端设计结论

### 2.1 认证策略

第一版不单独提供认证接口，不引入 JWT、不做登录态校验。

原因：

1. 项目仅自用
2. 当前前端登录页更多是角色切换和页面流程入口
3. 第一版更重要的是先打通任务、盲测、统计闭环

因此建议采用“轻量操作者信息”方案：

1. 前端在每个请求体里附带操作者信息
2. 后端只做最基础的角色判断，不做 token 校验

请求体中统一增加：

```json
{
  "operator": {
    "username": "admin01",
    "role": "admin"
  }
}
```

说明：

1. `operator` 只用于审计、记录创建人、做最基础权限判断
2. 后续如果要升级为正式系统，再把这部分替换成 JWT 即可

### 2.2 接口风格

所有接口统一为 `POST`。

这样做的好处是：

1. 前端调用方式统一
2. 查询条件、筛选条件、操作者信息都可以统一放在 body 里
3. 对当前原型开发更省事

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

错误响应建议：

```json
{
  "code": 4001,
  "message": "task not found",
  "data": null
}
```

### 2.3 上传策略

当前仅开放 Excel 上传，不开放 ZIP。

开放：

1. Prompt Excel 上传
2. 题目 Excel 上传
3. 测试数据 Excel 上传

预留但不开放：

1. ZIP 导入包上传

建议规则：

1. 当前只正式支持 `.xlsx`
2. `.xls` 暂不支持，避免额外引入旧版解析依赖
3. ZIP 接口保留路由名，但统一返回“功能未开放”

### 2.4 Python 3.6 兼容性

后端运行环境固定为 Python 3.6，因此依赖版本需要保守选择。

建议依赖版本：

1. `fastapi==0.78.0`
2. `uvicorn==0.16.0`
3. `python-multipart==0.0.5`
4. `openpyxl==3.0.10`

说明：

1. 根据 PyPI 页面，`fastapi 0.78.0` 支持 Python 3.6+
2. 根据 Uvicorn PyPI 页面提示，Python 3.6 需使用 `0.16.0`
3. `openpyxl 3.0.10` 可用于 `.xlsx` 读取

## 3. 后端目录规划

新建后端目录：

`prompt-blind-test-backend`

建议结构：

```text
prompt-blind-test-backend/
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── response.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── system.py
│   │   ├── tasks.py
│   │   ├── sessions.py
│   │   ├── uploads.py
│   │   ├── stats.py
│   │   └── ai.py
│   └── services/
│       ├── __init__.py
│       └── excel_parser.py
└── data/
    └── README.md
```

说明：

1. `app/api/` 放路由
2. `app/services/` 放 Excel 解析、统计、会话逻辑
3. `data/` 放 JSON 文件数据

## 4. 核心数据模型

### 4.1 Operator

```json
{
  "username": "admin01",
  "role": "admin"
}
```

### 4.2 Task

```json
{
  "id": 1,
  "name": "客服回复质量对比（V3 vs V4）",
  "description": "比较两组提示词在客服安抚回复中的表现差异",
  "status": "published",
  "visibility": "public",
  "question_limit": 49,
  "created_by": "admin01",
  "prompt_a_text": "......",
  "prompt_b_text": "......",
  "test_data_text": "......",
  "item_count": 12,
  "session_count": 35,
  "created_at": "2026-04-19T10:00:00+08:00",
  "updated_at": "2026-04-19T12:00:00+08:00"
}
```

字段建议：

1. `status`: `draft | unpublished | published`
2. `visibility`: `public | private`

### 4.3 TaskItem

```json
{
  "id": 101,
  "task_id": 1,
  "code": "Q001",
  "source_type": "text",
  "source_text": "用户投诉昨天买的商品今天降价了......",
  "images": [],
  "sort_order": 1
}
```

### 4.4 Session

```json
{
  "id": "s_20260419_0001",
  "task_id": 1,
  "username": "tester01",
  "status": "in_progress",
  "question_limit": 49,
  "answered_count": 3,
  "start_time": "2026-04-19T14:00:00+08:00",
  "end_time": null
}
```

### 4.5 SessionQuestionRecord

```json
{
  "id": "sq_001",
  "session_id": "s_20260419_0001",
  "slot_index": 1,
  "task_item_id": 101,
  "original_question": "请生成客服安抚回复",
  "test_data": "订单号xxx，商品xxx",
  "candidate_a": "......",
  "candidate_b": "......",
  "selected_option": "A",
  "actual_selected_prompt": "prompt_a",
  "judge_result": {
    "recommended_option": "B",
    "reason": "......"
  }
}
```

关键约束：

1. 前端只能拿到 `candidate_a` 和 `candidate_b`
2. `actual_selected_prompt` 只能由后端保存
3. 统计必须按真实 Prompt 归因

## 5. Excel 上传设计

### 5.1 Prompt Excel 上传

接口：

`POST /api/v1/upload/prompt_excel`

用途：

1. 上传任务 Prompt 配置
2. 解析出 Prompt A 和 Prompt B

推荐 Excel 模板：

| task_name | task_description | prompt_a | prompt_b |
| ---- | ---- | ---- | ---- |
| 客服回复质量对比 | 比较两组提示词效果 | 这里是 Prompt A | 这里是 Prompt B |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "task_name": "客服回复质量对比",
    "task_description": "比较两组提示词效果",
    "prompt_a_text": "这里是 Prompt A",
    "prompt_b_text": "这里是 Prompt B"
  }
}
```

### 5.2 题目 Excel 上传

接口：

`POST /api/v1/upload/item_excel`

用途：

1. 批量导入题目
2. 替代当前原型里 ZIP 导入的开放能力

推荐 Excel 模板：

| code | sort_order | source_type | source_text |
| ---- | ---- | ---- | ---- |
| Q001 | 1 | text | 用户投诉昨天买的商品今天降价了 |
| Q002 | 2 | text | 用户反馈快递延迟两天 |

说明：

1. 第一版只支持 `source_type=text`
2. 图片题先保留字段，不在第一版开放

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "item_count": 2,
    "items": [
      {
        "code": "Q001",
        "sort_order": 1,
        "source_type": "text",
        "source_text": "用户投诉昨天买的商品今天降价了"
      }
    ]
  }
}
```

### 5.3 测试数据 Excel 上传

接口：

`POST /api/v1/upload/test_data_excel`

用途：

1. 上传测试数据
2. 供会话生成时补充上下文

推荐 Excel 模板：

| data_key | data_value |
| ---- | ---- |
| order_id | 123456 |
| product_name | 手机壳 |
| complaint_reason | 昨天下单今天降价 |

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "row_count": 3,
    "preview_text": "order_id=123456\nproduct_name=手机壳\ncomplaint_reason=昨天下单今天降价"
  }
}
```

### 5.4 ZIP 上传预留

接口预留：

`POST /api/v1/upload/task_zip`

当前策略：

1. 路由预留
2. 返回“功能未开放”
3. 前端先不要接入

返回示例：

```json
{
  "code": 4003,
  "message": "zip upload is not enabled yet",
  "data": null
}
```

## 6. POST 接口清单

### 6.1 系统接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/system/ping` | 服务连通性检查 |

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
| POST | `/api/v1/task/item/update` | 修改单题 |
| POST | `/api/v1/task/item/delete` | 删除单题 |
| POST | `/api/v1/task/item/import_excel` | Excel 批量导入题目 |

### 6.4 上传接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/upload/prompt_excel` | 上传 Prompt Excel |
| POST | `/api/v1/upload/item_excel` | 上传题目 Excel |
| POST | `/api/v1/upload/test_data_excel` | 上传测试数据 Excel |
| POST | `/api/v1/upload/task_zip` | 预留 ZIP 上传接口，暂不开放 |

### 6.5 会话接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/session/start` | 开始测试 |
| POST | `/api/v1/session/detail` | 获取会话详情 |
| POST | `/api/v1/session/generate` | 生成候选回答 |
| POST | `/api/v1/session/vote` | 保存投票 |
| POST | `/api/v1/session/judge` | 大模型裁判 |
| POST | `/api/v1/session/finish` | 正常结束任务 |
| POST | `/api/v1/session/quit` | 中途退出并保留已答内容 |

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
| POST | `/api/v1/stats/dashboard_overview` | 获取后台统计概览 |

### 6.8 AI 接口

| 方法 | 路径 | 用途 |
| ---- | ---- | ---- |
| POST | `/api/v1/ai/prompt_generate` | 一键生成 Prompt |

## 7. 重点接口说明

### 7.1 获取任务列表

`POST /api/v1/task/list`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "filters": {
    "status": "published",
    "keyword": "客服",
    "mine": false
  }
}
```

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
    "question_limit": 49,
    "prompt_a_text": "......",
    "prompt_b_text": "......",
    "test_data_text": ""
  }
}
```

### 7.3 开始测试

`POST /api/v1/session/start`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "task_id": 1,
  "question_limit": 49
}
```

### 7.4 生成候选回答

`POST /api/v1/session/generate`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "session_id": "s_20260419_0001",
  "slot_index": 1,
  "original_question": "请生成客服安抚回复",
  "test_data": "订单号123，用户反馈降价",
  "force_regenerate": false
}
```

响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "question_record_id": "sq_001",
    "candidate_a": "您好，很抱歉给您带来不好的体验......",
    "candidate_b": "非常抱歉让您遇到这样的情况......"
  }
}
```

说明：

1. 后端在内部完成 Prompt A/B 到 A/B 候选回答的随机映射
2. 前端不能拿到真实映射

### 7.5 保存投票

`POST /api/v1/session/vote`

请求示例：

```json
{
  "operator": {
    "username": "tester01",
    "role": "tester"
  },
  "session_id": "s_20260419_0001",
  "question_record_id": "sq_001",
  "selected_option": "A"
}
```

要求：

1. 必须幂等
2. 重复提交时以后一次为准

## 8. 文件存储建议

```text
data/
├── tasks.json
├── sessions.json
└── uploads/
```

当前 MVP 实现：

1. `tasks.json` 保存任务主信息与题目列表
2. `sessions.json` 保存会话明细、投票、裁判结果和真实映射
3. `uploads/` 预留为上传文件目录

如果后续数据量变大，再拆分为：

1. `tasks/` 保存任务主信息
2. `task_items/` 保存题目列表
3. `sessions/` 保存会话明细、投票、裁判结果和真实映射
4. `stats/` 保存统计缓存
5. `uploads/` 保存上传过的 Excel 原文件

## 9. MVP 开发建议

第一阶段先做以下最小闭环：

1. `POST /api/v1/task/list`
2. `POST /api/v1/task/create`
3. `POST /api/v1/task/detail`
4. `POST /api/v1/task/update`
5. `POST /api/v1/task/item/create`
6. `POST /api/v1/task/item/import_excel`
7. `POST /api/v1/session/start`
8. `POST /api/v1/session/generate`
9. `POST /api/v1/session/vote`
10. `POST /api/v1/stats/task_overview`
11. `POST /api/v1/ai/prompt_generate`

第二阶段再补：

1. `session/judge`
2. `history/*`
3. `upload/task_zip`

## 10. 实现注意点

1. 由于不做认证，所有请求都要做基础参数校验，避免缺少 `operator`
2. 因为全部使用 `POST`，接口命名要足够清晰，避免语义混乱
3. Excel 上传第一版只支持 `.xlsx`
4. ZIP 路由保留，但必须明确返回“未开放”
5. Python 3.6 下不要使用新语法，例如 `list[str]`、`|` 联合类型、`match-case`
