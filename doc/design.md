# Prompt盲选测试平台技术设计文档

## 1. 技术栈选择

### 1.1 前端技术栈

- **框架**：Vue 2
- **构建工具**：Vue CLI
- **状态管理**：组件内状态管理
- 路由： Vue Router
- **HTTP客户端**：Axios

### 1.2 后端技术栈

- **语言**：Python 3.6
- **Web框架**：FastAPI
- **认证**：JWT
- **AI模型集成**：用于prompt生成和测试结果分析
- **存储**：结构化文件存储（JSON格式）

### 1.3 存储方案

- **文件格式**：JSON
- **存储结构**：结构化文件系统
- **目录组织**：按功能模块划分

### 1.4 部署方案

- **前端**：静态文件部署
- **后端**：Python虚拟环境
- **服务器**：本地服务器或云服务

## 2. 系统架构设计

### 2.1 架构图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     前端应用     │────>│     后端API      │────>│  文件系统存储    │
│       Vue2│     │      FastAPI + Python │     │   JSON文件      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 2.2 模块划分

- **前端模块**：
  - 认证模块：处理用户注册、登录
  - 测试模块：处理盲选测试流程
  - 排行榜模块：展示prompt排名
  - 个人中心模块：管理用户信息
  - 公共组件：复用组件
- **后端模块**：
  - 认证模块：处理用户认证和授权
  - Prompt模块：管理prompt的CRUD操作
  - 测试模块：处理测试流程和结果
  - 投票模块：处理用户投票
  - 排行榜模块：计算和生成排行榜
  - 存储模块：处理文件系统操作

### 2.3 数据流向

1. **用户登录流程**：
   - 访问首页 → 点击登录 → 填写凭证 → 验证 → 进入个人中心
2. **盲选测试流程**：
   - 登录 → 选择测试任务 → 系统生成测试轮次（奇数个问题） → 逐题测试投票 → 保存题目测试结果 → 展示结果和分析
3. **Prompt管理流程**：
   - 登录 → 进入个人中心 → 一键生成prompt

## 3. 前端设计

### 3.1 目录结构

```
/
├── src/
│   ├── components/      # 公共组件
│   │   └── Sidebar.vue  # 侧边栏组件
│   ├── views/           # 页面组件
│   │   ├── admin/       # 管理员视图
│   │   │   ├── PromptGenerate.vue  # Prompt一键生成
│   │   │   ├── Stats.vue            # 统计分析
│   │   │   ├── TaskEditor.vue       # 任务编辑
│   │   │   └── TaskManagement.vue   # 任务管理
│   │   ├── auth/        # 认证视图
│   │   │   └── Login.vue            # 登录页面
│   │   └── tester/      # 测试员视图
│   │       ├── History.vue          # 测试历史
│   │       ├── ImportTaskEditor.vue # 导入任务编辑
│   │       ├── TaskDetail.vue       # 任务详情
│   │       ├── TaskList.vue         # 任务列表
│   │       └── TestSession.vue      # 测试会话
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML模板
├── package.json         # 依赖配置
├── vue.config.js        # Vue CLI配置
└── babel.config.js      # Babel配置
```

### 3.2 核心组件

| 组件 | 功能 | 位置 |
|------|------|------|
| Login | 登录页面 | views/auth/Login.vue |
| Sidebar | 侧边栏导航 | components/Sidebar.vue |
| TaskList | 任务列表 | views/tester/TaskList.vue |
| TaskDetail | 任务详情 | views/tester/TaskDetail.vue |
| TestSession | 测试会话 | views/tester/TestSession.vue |
| History | 测试历史 | views/tester/History.vue |
| TaskManagement | 任务管理 | views/admin/TaskManagement.vue |
| TaskEditor | 任务编辑 | views/admin/TaskEditor.vue |
| Stats | 统计分析 | views/admin/Stats.vue |
| PromptGenerate | Prompt一键生成 | views/admin/PromptGenerate.vue |
| ImportTaskEditor | 导入任务编辑 | views/tester/ImportTaskEditor.vue |

### 3.3 页面设计

| 视图 | 组件 | 描述 |
|------|------|------|
| 登录视图 | Login | 用户登录页面 |
| 测试员任务列表 | TaskList | 测试员查看和选择测试任务 |
| 测试员任务详情 | TaskDetail | 测试员查看任务详细信息 |
| 测试会话 | TestSession | 测试员进行盲选测试的界面 |
| 测试历史 | History | 测试员查看测试历史记录 |
| 导入任务编辑 | ImportTaskEditor | 测试员导入和编辑测试任务 |
| 管理员任务管理 | TaskManagement | 管理员管理测试任务 |
| 管理员任务编辑 | TaskEditor | 管理员编辑测试任务 |
| 管理员统计分析 | Stats | 管理员查看测试统计数据 |
| 管理员Prompt生成 | PromptGenerate | 管理员一键生成Prompt |

### 3.4 状态管理

项目使用组件内状态管理，主要状态包括：

**App.vue 中的状态：**

- `isLoggedIn`：用户登录状态
- `currentUser`：当前用户信息（包含角色）
- `currentView`：当前视图
- `selectedTaskId`：当前选中的任务ID
- `currentSession`：当前测试会话
- `currentQuestionIndex`：当前问题索引
- `selectedAnswer`：用户选择的答案
- `userInputs`：用户输入
- `historyOperations`：历史操作记录
- `adminManagementTasks`：管理员管理的任务
- `adminTasks`：管理员测试任务
- `testerTasks`：测试员任务

**TestSession.vue 中的状态：**

- 测试会话相关状态
- 大模型裁判结果
- 测试数据

**其他组件状态：**

- 各组件根据需要维护自己的状态

### 3.5 API服务

当前项目未使用API服务，而是使用本地模拟数据：

- **数据存储**：在App.vue中维护本地模拟数据
- **任务数据**：包含管理员任务、测试员任务等
- **测试会话**：本地维护测试会话数据
- **历史记录**：本地记录测试历史操作

**模拟数据结构：**

- 任务数据：包含id、name、description、promptA、promptB、items等
- 测试会话：包含id、taskId、questions、answers、userInputs等
- 历史操作：包含id、type、userId、taskId、timestamp等

**未来扩展**：

- 可根据需要添加API服务，连接后端FastAPI接口

## 4. 后端设计

### 4.1 目录结构

```
backend/
├── app/
│   ├── api/             # API路由
│   │   ├── auth.py      # 认证相关API
│   │   ├── prompt.py    # Prompt相关API
│   │   ├── test.py      # 测试相关API
│   │   ├── vote.py      # 投票相关API
│   │   ├── leaderboard.py # 排行榜相关API
│   │   └── ai.py        # AI相关API
│   ├── services/        # 业务逻辑
│   │   ├── auth.py      # 认证服务
│   │   ├── prompt.py    # Prompt服务
│   │   ├── test.py      # 测试服务
│   │   ├── vote.py      # 投票服务
│   │   ├── leaderboard.py # 排行榜服务
│   │   └── ai.py        # AI服务
│   ├── models/          # 数据模型
│   │   ├── user.py      # 用户模型
│   │   ├── prompt.py    # Prompt模型
│   │   ├── test.py      # 测试模型
│   │   ├── vote.py      # 投票模型
│   │   └── ai.py        # AI模型
│   ├── schemas/         # 数据验证
│   │   ├── user.py      # 用户相关Schema
│   │   ├── prompt.py    # Prompt相关Schema
│   │   ├── test.py      # 测试相关Schema
│   │   ├── vote.py      # 投票相关Schema
│   │   └── ai.py        # AI相关Schema
│   ├── storage/         # 存储服务
│   │   ├── base.py      # 存储基类
│   │   ├── user.py      # 用户存储
│   │   ├── prompt.py    # Prompt存储
│   │   ├── test.py      # 测试存储
│   │   └── vote.py      # 投票存储
│   ├── utils/           # 工具函数
│   │   ├── jwt.py       # JWT工具
│   │   ├── password.py  # 密码工具
│   │   ├── file.py      # 文件操作工具
│   │   └── ai.py        # AI工具
│   ├── main.py          # 应用入口
│   └── config.py        # 配置文件
├── data/                # 数据存储目录
│   ├── users/           # 用户数据
│   ├── prompts/         # Prompt数据
│   ├── test_sessions/   # 测试会话数据
│   ├── test_results/    # 测试结果数据
│   └── votes/           # 投票数据
├── requirements.txt     # 依赖配置
└── .env                 # 环境变量
```

### 4.2 核心服务

#### 4.2.1 认证服务

```python
# services/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.storage.user import UserStorage
from app.schemas.user import UserCreate, UserLogin, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.user_storage = UserStorage()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
        return encoded_jwt
    
    def register(self, user_data: UserCreate) -> User:
        # 检查用户是否已存在
        existing_user = self.user_storage.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # 创建新用户
        hashed_password = self.get_password_hash(user_data.password)
        user = self.user_storage.create({
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        })
        return user
    
    def login(self, user_data: UserLogin) -> dict:
        # 查找用户
        user = self.user_storage.get_by_email(user_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # 验证密码
        if not self.verify_password(user_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # 创建访问令牌
        access_token = self.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    
    def get_current_user(self, email: str) -> User:
        user = self.user_storage.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        return user
```

#### 4.2.2 存储服务

```python
# storage/base.py
import json
import os
from typing import List, Dict, Optional, Any

class BaseStorage:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _get_file_path(self, item_id: str) -> str:
        return os.path.join(self.base_dir, f"{item_id}.json")
    
    def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        item_id = str(len(os.listdir(self.base_dir)) + 1)
        item["id"] = item_id
        file_path = self._get_file_path(item_id)
        with open(file_path, "w") as f:
            json.dump(item, f, indent=2)
        return item
    
    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_file_path(item_id)
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as f:
            return json.load(f)
    
    def list(self) -> List[Dict[str, Any]]:
        items = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.base_dir, filename)
                with open(file_path, "r") as f:
                    items.append(json.load(f))
        return items
    
    def update(self, item_id: str, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        file_path = self._get_file_path(item_id)
        if not os.path.exists(file_path):
            return None
        item["id"] = item_id
        with open(file_path, "w") as f:
            json.dump(item, f, indent=2)
        return item
    
    def delete(self, item_id: str) -> bool:
        file_path = self._get_file_path(item_id)
        if not os.path.exists(file_path):
            return False
        os.remove(file_path)
        return True

# storage/user.py
from app.storage.base import BaseStorage
from typing import Optional

class UserStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/users")
    
    def get_by_email(self, email: str) -> Optional[dict]:
        users = self.list()
        for user in users:
            if user.get("email") == email:
                return user
        return None
    
    def get_by_username(self, username: str) -> Optional[dict]:
        users = self.list()
        for user in users:
            if user.get("username") == username:
                return user
        return None

# storage/prompt.py
from app.storage.base import BaseStorage
from typing import List

class PromptStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/prompts")
    
    def get_by_category(self, category: str) -> List[dict]:
        prompts = self.list()
        return [p for p in prompts if p.get("category") == category]
    
    def get_by_tags(self, tags: List[str]) -> List[dict]:
        prompts = self.list()
        return [p for p in prompts if any(tag in p.get("tags", []) for tag in tags)]

# storage/test.py
from app.storage.base import BaseStorage
from typing import List

class TestSessionStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/test_sessions")
    
    def get_by_user(self, user_id: str) -> List[dict]:
        sessions = self.list()
        return [s for s in sessions if s.get("user_id") == user_id]

class TestResultStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/test_results")
    
    def get_by_session(self, session_id: str) -> List[dict]:
        results = self.list()
        return [r for r in results if r.get("session_id") == session_id]

# storage/vote.py
from app.storage.base import BaseStorage
from typing import List

class VoteStorage(BaseStorage):
    def __init__(self):
        super().__init__("data/votes")
    
    def get_by_user(self, user_id: str) -> List[dict]:
        votes = self.list()
        return [v for v in votes if v.get("user_id") == user_id]
    
    def get_by_test_result(self, test_result_id: str) -> List[dict]:
        votes = self.list()
        return [v for v in votes if v.get("test_result_id") == test_result_id]
```

#### 4.2.3 测试服务

```python
# services/test.py
import random
from datetime import datetime
from typing import List, Dict, Any
from app.storage.test import TestSessionStorage, TestResultStorage
from app.storage.prompt import PromptStorage
from app.schemas.test import TestSessionCreate, TestResultCreate

class TestService:
    def __init__(self):
        self.session_storage = TestSessionStorage()
        self.result_storage = TestResultStorage()
        self.prompt_storage = PromptStorage()
    
    def start_test(self, user_id: str, category: str) -> Dict[str, Any]:
        # 获取该分类下的所有prompt
        prompts = self.prompt_storage.get_by_category(category)
        if len(prompts) < 2:
            raise ValueError("Not enough prompts in this category")
        
        # 创建测试会话
        session = self.session_storage.create({
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None
        })
        
        # 生成3个测试问题（奇数个问题）
        test_results = []
        test_prompts = []
        
        for _ in range(3):
            # 随机选择两个prompt
            prompt1, prompt2 = random.sample(prompts, 2)
            
            # 创建测试结果记录
            test_result = self.result_storage.create({
                "session_id": session["id"],
                "prompt1_id": prompt1["id"],
                "prompt2_id": prompt2["id"],
                "winner_id": None,
                "created_at": datetime.utcnow().isoformat()
            })
            
            test_results.append(test_result)
            test_prompts.append({"prompt1": prompt1, "prompt2": prompt2})
        
        return {
            "session": session,
            "test_results": test_results,
            "test_prompts": test_prompts
        }
    
    def submit_vote(self, user_id: str, test_result_id: str, winner_id: str) -> Dict[str, Any]:
        # 获取测试结果
        test_result = self.result_storage.get(test_result_id)
        if not test_result:
            raise ValueError("Test result not found")
        
        # 更新测试结果
        test_result["winner_id"] = winner_id
        updated_test_result = self.result_storage.update(test_result_id, test_result)
        
        # 检查测试会话是否完成
        session = self.session_storage.get(test_result["session_id"])
        if session:
            # 获取该会话的所有测试结果
            all_results = self.result_storage.get_by_session(session["id"])
            # 检查是否所有测试结果都已完成
            all_completed = all(result.get("winner_id") is not None for result in all_results)
            
            if all_completed:
                session["completed_at"] = datetime.utcnow().isoformat()
                self.session_storage.update(session["id"], session)
        
        return updated_test_result
    
    def get_user_tests(self, user_id: str) -> List[Dict[str, Any]]:
        sessions = self.session_storage.get_by_user(user_id)
        return sessions
    
    def get_test_results(self, session_id: str) -> List[Dict[str, Any]]:
        results = self.result_storage.get_by_session(session_id)
        return results
```

#### 4.2.4 AI服务

```python
# services/ai.py
from typing import Dict, Any, List
from app.storage.test import TestSessionStorage, TestResultStorage
from app.storage.prompt import PromptStorage

class AIService:
    def __init__(self):
        self.session_storage = TestSessionStorage()
        self.result_storage = TestResultStorage()
        self.prompt_storage = PromptStorage()
    
    def analyze_test_results(self, test_session_id: str, user_id: str) -> Dict[str, Any]:
        # 获取测试会话
        session = self.session_storage.get(test_session_id)
        if not session or session.get("user_id") != user_id:
            raise ValueError("Test session not found or access denied")
        
        # 获取测试结果
        test_results = self.result_storage.get_by_session(test_session_id)
        if not test_results:
            raise ValueError("No test results found")
        
        # 分析测试结果
        prompt_wins = {}
        total_votes = len(test_results)
        
        for result in test_results:
            winner_id = result.get("winner_id")
            if winner_id:
                if winner_id not in prompt_wins:
                    prompt_wins[winner_id] = 0
                prompt_wins[winner_id] += 1
        
        # 获取prompt详情
        prompt_details = {}
        for prompt_id, wins in prompt_wins.items():
            prompt = self.prompt_storage.get(prompt_id)
            if prompt:
                prompt_details[prompt_id] = {
                    "content": prompt.get("content"),
                    "category": prompt.get("category"),
                    "wins": wins,
                    "win_rate": wins / total_votes
                }
        
        # 生成分析报告
        analysis = {
            "test_session_id": test_session_id,
            "total_tests": total_votes,
            "prompt_performance": prompt_details,
            "recommendations": self._generate_recommendations(prompt_details)
        }
        
        return analysis
    
    def _generate_recommendations(self, prompt_details: Dict[str, Any]) -> List[str]:
        # 生成优化建议
        recommendations = []
        
        # 分析最佳prompt的特点
        if prompt_details:
            best_prompt_id = max(prompt_details, key=lambda x: prompt_details[x]["win_rate"])
            best_prompt = prompt_details[best_prompt_id]
            
            recommendations.append(f"最佳Prompt: {best_prompt['content']}")
            recommendations.append(f"胜率: {best_prompt['win_rate']:.2f}")
            recommendations.append("建议分析该Prompt的结构和用词，应用到其他Prompt中")
        
        return recommendations
```

#### 4.2.5 Prompt服务（支持一键生成）

```python
# services/prompt.py
from datetime import datetime
from typing import List, Dict, Any
from app.storage.prompt import PromptStorage
from app.schemas.prompt import PromptCreate

class PromptService:
    def __init__(self):
        self.prompt_storage = PromptStorage()
    
    def create(self, prompt_data: PromptCreate, author_id: str) -> Dict[str, Any]:
        # 创建新prompt
        prompt = self.prompt_storage.create({
            "content": prompt_data.content,
            "category": prompt_data.category,
            "tags": prompt_data.tags,
            "author_id": author_id,
            "created_at": datetime.utcnow().isoformat()
        })
        return prompt
    
    def list(self, category: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        # 获取prompt列表
        if category:
            return self.prompt_storage.get_by_category(category)
        elif tags:
            return self.prompt_storage.get_by_tags(tags)
        else:
            return self.prompt_storage.list()
    
    def get(self, prompt_id: str) -> Dict[str, Any]:
        # 获取单个prompt
        return self.prompt_storage.get(prompt_id)
    
    def generate(self, category: str, purpose: str) -> Dict[str, Any]:
        # 一键生成prompt
        # 这里可以集成AI模型来生成prompt
        # 暂时使用模板生成
        templates = {
            "general": "请详细描述{purpose}，提供具体的步骤和示例。",
            "coding": "请编写{purpose}的代码，包括详细的注释和使用示例。",
            "creative": "请创作{purpose}，要求内容新颖，有创意。",
            "analytical": "请分析{purpose}，提供数据支持和深入见解。"
        }
        
        template = templates.get(category, templates["general"])
        generated_content = template.format(purpose=purpose)
        
        # 存储生成的prompt
        prompt = self.prompt_storage.create({
            "content": generated_content,
            "category": category,
            "tags": [category, "generated"],
            "author_id": "system",
            "created_at": datetime.utcnow().isoformat()
        })
        
        return prompt
```

### 4.3 API设计

#### 4.3.1 认证API

```python
# api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserLogin, User, Token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
auth_service = AuthService()

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth_service.get_current_user(email)
    if user is None:
        raise credentials_exception
    return User(**user)

@router.post("/register", response_model=User)
def register(user_data: UserCreate):
    try:
        user = auth_service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token_data = auth_service.login(UserLogin(email=form_data.username, password=form_data.password))
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/profile", response_model=User)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

#### 4.3.2 Prompt API

```python
# api/prompt.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.services.prompt import PromptService
from app.schemas.prompt import PromptCreate, Prompt, PromptListParams
from app.api.auth import get_current_user
from app.schemas.user import User

router = APIRouter(prefix="/prompt", tags=["prompt"])
prompt_service = PromptService()

@router.post("/upload", response_model=Prompt)
def upload_prompt(prompt_data: PromptCreate, current_user: User = Depends(get_current_user)):
    try:
        prompt = prompt_service.create(prompt_data, current_user.id)
        return prompt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate", response_model=Prompt)
def generate_prompt(
    category: str = Query(..., description="Prompt category"),
    purpose: str = Query(..., description="Prompt purpose"),
    current_user: User = Depends(get_current_user)
):
    try:
        prompt = prompt_service.generate(category, purpose)
        return prompt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=List[Prompt])
def list_prompts(params: PromptListParams = Depends()):
    prompts = prompt_service.list(params.category, params.tags)
    return prompts

@router.get("/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    prompt = prompt_service.get(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
```

#### 4.3.3 测试API

```python
# api/test.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.test import TestService
from app.schemas.test import TestSessionCreate, TestResult, VoteCreate
from app.api.auth import get_current_user
from app.schemas.user import User

router = APIRouter(prefix="/test", tags=["test"])
test_service = TestService()

@router.post("/start", response_model=dict)
def start_test(test_data: TestSessionCreate, current_user: User = Depends(get_current_user)):
    try:
        test_session = test_service.start_test(current_user.id, test_data.category)
        return test_session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vote", response_model=TestResult)
def submit_vote(vote_data: VoteCreate, current_user: User = Depends(get_current_user)):
    try:
        test_result = test_service.submit_vote(current_user.id, vote_data.test_result_id, vote_data.winner_id)
        return test_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/results", response_model=List[dict])
def get_results(current_user: User = Depends(get_current_user)):
    tests = test_service.get_user_tests(current_user.id)
    return tests

@router.get("/results/{session_id}", response_model=List[dict])
def get_test_session_results(session_id: str, current_user: User = Depends(get_current_user)):
    try:
        results = test_service.get_test_results(session_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 4.3.4 排行榜API

```python
# api/leaderboard.py
from fastapi import APIRouter, Query
from typing import List
from app.services.leaderboard import LeaderboardService
from app.schemas.leaderboard import LeaderboardItem

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
leaderboard_service = LeaderboardService()

@router.get("", response_model=List[LeaderboardItem])
def get_leaderboard(
    category: str = Query(None, description="Prompt category"),
    sort_by: str = Query("quality", description="Sort by: quality,热度,created_at")
):
    leaderboard = leaderboard_service.get_leaderboard(category, sort_by)
    return leaderboard
```

#### 4.3.5 AI API

```python
# api/ai.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.ai import AIService
from app.api.auth import get_current_user
from app.schemas.user import User

router = APIRouter(prefix="/ai", tags=["ai"])
ai_service = AIService()

@router.get("/analyze", response_model=Dict[str, Any])
def analyze_test_results(
    test_session_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        analysis = ai_service.analyze_test_results(test_session_id, current_user.id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 5. 数据模型设计

### 5.1 用户模型

```python
# models/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
```

### 5.2 Prompt模型

```python
# models/prompt.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PromptBase(BaseModel):
    content: str
    category: str
    tags: List[str]

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: str
    author_id: str
    created_at: str
    
    class Config:
        from_attributes = True

class PromptListParams(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
```

### 5.3 测试模型

```python
# models/test.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestSessionCreate(BaseModel):
    category: str

class TestSession(BaseModel):
    id: str
    user_id: str
    created_at: str
    completed_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class TestResult(BaseModel):
    id: str
    session_id: str
    prompt1_id: str
    prompt2_id: str
    winner_id: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

class VoteCreate(BaseModel):
    test_result_id: str
    winner_id: str
```

### 5.4 投票模型

```python
# models/vote.py
from pydantic import BaseModel
from datetime import datetime

class Vote(BaseModel):
    id: str
    user_id: str
    test_result_id: str
    vote: str
    created_at: str
    
    class Config:
        from_attributes = True
```

### 5.5 排行榜模型

```python
# models/leaderboard.py
from pydantic import BaseModel

class LeaderboardItem(BaseModel):
    id: str
    content: str
    category: str
    score: float
    votes: int
    created_at: str
    
    class Config:
        from_attributes = True
```

### 5.6 AI模型

```python
# models/ai.py
from pydantic import BaseModel
from typing import List, Dict, Any

class AnalysisRequest(BaseModel):
    test_session_id: str

class AnalysisResult(BaseModel):
    test_session_id: str
    total_tests: int
    prompt_performance: Dict[str, Any]
    recommendations: List[str]

class PromptGenerateRequest(BaseModel):
    category: str
    purpose: str
```

## 6. 部署与配置

### 6.1 前端部署

1. **安装依赖**：
   ```bash
   cd frontend
   npm install
   ```
2. **构建静态文件**：
   ```bash
   npm run build
   ```
3. **部署静态文件**：
   - 将 `dist` 目录部署到静态文件服务器
   - 配置服务器支持SPA路由（ fallback到index.html）

### 6.2 后端部署

1. **创建虚拟环境**：
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **配置环境变量**：
   - 创建 `.env` 文件
   - 设置 `SECRET_KEY` 等配置
4. **创建数据目录**：
   ```bash
   mkdir -p data/users data/prompts data/test_sessions data/test_results data/votes
   ```
5. **运行应用**：
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 6.3 配置文件

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATA_DIR: str = "data"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 7. 测试策略

### 7.1 前端测试

- **单元测试**：测试组件功能
  ```bash
  npm test
  ```
- **端到端测试**：测试完整流程
  ```bash
  npm run e2e
  ```

### 7.2 后端测试

- **单元测试**：测试服务功能
  ```bash
  pytest
  ```
- **API测试**：测试API接口
  ```bash
  pytest tests/api
  ```

### 7.3 性能测试

- **负载测试**：测试高并发场景
  ```bash
  locust -f tests/performance/locustfile.py
  ```

## 8. 安全考虑

### 8.1 认证与授权

- 使用JWT进行身份认证
- 密码加密存储
- 权限控制确保用户只能访问自己的数据

### 8.2 数据安全

- 敏感数据加密存储
- 文件操作权限控制
- 输入验证防止注入攻击

### 8.3 网络安全

- 使用HTTPS协议
- CORS配置限制跨域访问
- 防止CSRF攻击

## 9. 监控与维护

### 9.1 日志记录

- 关键操作日志
- 错误日志
- 访问日志

### 9.2 性能监控

- API响应时间
- 系统资源使用情况
- 错误率监控

### 9.3 数据备份

- 定期备份数据文件
- 灾难恢复方案

## 10. 技术挑战与解决方案

| 挑战         | 解决方案                      |
| ---------- | ------------------------- |
| 文件系统并发操作   | 实现文件锁机制，确保操作原子性           |
| 数据一致性      | 事务性操作，确保数据完整              |
| 性能优化       | 缓存机制，减少文件IO操作             |
| 扩展性        | 模块化设计，支持功能扩展              |
| 安全性        | 加密存储，权限控制                 |
| AI模型集成     | 使用轻量级AI模型，确保响应速度          |
| Prompt生成质量 | 结合模板和AI技术，提高生成质量          |
| 测试结果分析     | 设计有效的分析算法，提供有价值的 insights |

## 11. 未来扩展

- **多语言支持**：添加国际化功能
- **AI辅助分析**：集成AI模型分析测试结果
- **社区功能**：添加用户交流和分享功能
- **API开放**：提供第三方集成接口
- **移动应用**：开发移动端应用

## 12. 结论

本技术设计文档详细说明了Prompt盲选测试平台的技术实现方案，包括技术栈选择、系统架构、代码结构和部署方案。通过Vue 3前端和Python FastAPI后端的组合，以及文件系统存储方案，实现了一个功能完整、架构清晰的prompt盲选测试平台。该设计既满足了用户的需求，又考虑了系统的可扩展性和可维护性，为平台的开发和后续迭代提供了明确的技术指导。
