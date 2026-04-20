# Prompt Blind Test Backend

这是一个为当前 Prompt 盲测前端准备的本地后端实现，目标是：

1. 基于 Python 3.6
2. 优先兼容 Python 3.6.10
3. 所有业务接口统一为 `POST`
4. 第一版不做 JWT 认证
5. 题目与测试数据当前仅开放 `.xlsx` 文件上传
6. ZIP 上传接口预留但不开放
7. Prompt 图片保存到本地目录

## 运行环境

1. Python 3.6.10
2. 建议使用本地 conda 环境 `python36`

## 当前运行方式

当前仓库内提供两种后端入口：

1. `simple_server.py`
   使用 Python 标准库实现，可直接在 `Python 3.6.10` 下运行，不依赖外部包
2. `app/main.py`
   保留 FastAPI 版本入口，便于后续切回框架化实现

```bash
/Users/shala/opt/anaconda3/envs/python36/bin/python simple_server.py
```

服务默认监听 `http://127.0.0.1:8000`。

## FastAPI 依赖

如果后续网络环境允许，也可以安装依赖后运行 FastAPI 版本：

```bash
/Users/shala/opt/anaconda3/envs/python36/bin/python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 自测

仓库内提供了基于 `Python 3.6.10` 的 smoke test：

```bash
/Users/shala/opt/anaconda3/envs/python36/bin/python smoke_test.py
```

这会自动启动本地服务，并依次验证：

1. 探活
2. 任务列表
3. 开始会话
4. 逐题生成
5. 投票保存
6. 模型裁判
7. 会话结束
8. 任务统计

## 目录说明

- `simple_server.py`：当前可直接运行的 Python 3.6 服务入口
- `smoke_test.py`：本地接口自测脚本
- `app/main.py`：FastAPI 入口
- `app/api/`：路由定义
- `app/services/`：任务、会话、Excel、JSON 存储服务
- `data/tasks.json`：任务主数据
- `data/sessions.json`：会话与作答数据
- `data/uploads/prompts/`：Prompt 图片本地存储目录

## 当前已实现能力

1. 系统探活接口
2. 任务、会话、历史、统计、AI 相关的 POST 接口
3. Prompt 文字配置与本地图片存储
4. `.xlsx` 题目 / 测试数据上传解析
5. ZIP 上传禁用返回
6. JSON 文件持久化存储
7. 前端联调所需的基础闭环

## 说明

当前版本是 MVP，可支撑本地自测和前后端联调。真实模型调用、数据库化存储、认证和更细的统计缓存仍可在下一阶段继续增强。
