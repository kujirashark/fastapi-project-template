# FastAPI 分层架构最佳实践模板

> FastAPI + Dependency-Injector + SQLAlchemy 2.0(异步)+ MySQL 的多用户博客示例项目

## 技术栈

| 层 | 技术 |
|---|---|
| Web 框架 | FastAPI 0.115+ |
| 依赖注入 | dependency-injector 4.41+ |
| ORM | SQLAlchemy 2.0(异步) |
| 数据库 | MySQL 8.0(aiomysql) |
| 数据迁移 | Alembic |
| 鉴权 | JWT + bcrypt |
| 配置 | pydantic-settings |
| 容器化 | Docker + docker-compose |

## 分层架构

本项目采用经典的分层架构,**每层都拆分为 `base/`(接口)和 `impl/`(实现)**:

```
src/app/
├── core/                      # 横切关注点:配置、数据库、安全、异常
├── domain/                    # 领域层:ORM 实体 + Pydantic DTO
│   ├── entities/              # SQLAlchemy 实体
│   └── schemas/               # Pydantic 输入/输出模型
├── repository/                # 仓储层:封装所有数据库操作
│   ├── base/                  # Protocol 接口
│   └── impl/                  # SQLAlchemy 实现
├── service/                   # 业务逻辑层:领域规则
│   ├── base/                  # Protocol 接口
│   └── impl/                  # 业务实现
└── api/                       # 路由层:FastAPI Router + Depends
```

**依赖方向(自上而下):** `api → service → repository → domain`,通过 DI 容器装配,各层不直接依赖具体实现,只依赖 `Protocol` 接口。

## 快速开始

### 方式一:Docker(推荐)

```bash
# 1. 复制环境变量
cp .env.example .env

# 2. 一键启动(自动跑迁移 + 启动应用)
docker-compose up --build
```

启动后访问:
- API 文档:http://localhost:8000/docs
- ReDoc:http://localhost:8000/redoc

### 方式二:本地开发

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 装依赖(推荐用 uv)
pip install -e ".[dev]"

# 3. 启动一个本地 MySQL(或者改 .env 里的 DB_HOST 指向你的 MySQL)

# 4. 跑迁移
alembic upgrade head

# 5. 启动服务
uvicorn app.main:app --reload --app-dir src
```

## 业务流程示例

以"创建文章"为例,展示各层协作:

```
HTTP POST /api/v1/posts
        │
        ▼
┌────────────────────────────────────┐
│  api/v1/posts.py                  │  1. 解析请求体 → PostCreate
│     ├── Depends(IUserService)       │
│     └── Depends(IPostService)     │  2. 从容器拿到 service 实例
└────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│  service/impl/post_service.py     │  3. 业务校验:
│     def create(post, author)      │     - 作者是否存在
│                                   │     - 分类是否存在
└────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│  repository/impl/post_repository  │  4. 持久化:
│     async def add(post)           │     INSERT INTO posts ...
└────────────────────────────────────┘
        │
        ▼
    MySQL 数据库
```

**关键点:** API 层从不直接 import Service 实现类,所有依赖都通过 `Depends(Provide[Container.post_service])` 从容器获取。

## 核心设计

### 1. Protocol 接口 + DI 解耦

```python
# repository/base/user.py
from typing import Protocol

class IUserRepository(Protocol):
    async def get(self, id: int) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def add(self, user: User) -> None: ...

# repository/impl/user_repository.py
class SQLAlchemyUserRepository:
    """实现 IUserRepository,通过 SQLAlchemy 操作"""
    ...

# containers.py
class Container(DeclarativeContainer):
    user_repository = Factory(SQLAlchemyUserRepository, session=db_session)
```

测试时只需替换 Factory 指向 mock 类,完全不动业务代码。

### 2. 通用 Repository 基类

`IBaseRepository[T]` 提供通用的 `get / list / add / delete`,各实体接口继承它再扩展:

```python
class IUserRepository(IBaseRepository[User], Protocol):
    async def get_by_email(self, email: str) -> User | None: ...
```

### 3. 异步 Session 生命周期

- 容器提供 `db_session` Provider(`Scoped`,每个请求一个新 session)
- API 层用 `Depends(get_db_session)` 拿到 session
- `post_service` 接收 session 作为参数,事务边界由 API 层统一控制

## 业务实体

| 实体 | 说明 |
|---|---|
| `User` | 多用户,bcrypt 密码哈希,登录返回 JWT |
| `Post` | 文章,关联 `author`(User)、`category`(Category)、`tags`(多对多) |
| `Category` | 分类,一对多关联 Post |
| `Tag` | 标签,多对多关联 Post |

## API 路由速查

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | `/api/v1/auth/register` | 注册 | 否 |
| POST | `/api/v1/auth/login` | 登录获取 JWT | 否 |
| GET | `/api/v1/users/me` | 获取当前用户 | 是 |
| GET | `/api/v1/posts` | 文章列表(分页+搜索) | 否 |
| POST | `/api/v1/posts` | 创建文章 | 是 |
| GET | `/api/v1/posts/{id}` | 文章详情 | 否 |
| PUT | `/api/v1/posts/{id}` | 更新文章 | 是(作者本人) |
| DELETE | `/api/v1/posts/{id}` | 删除文章 | 是(作者本人) |
| GET | `/api/v1/categories` | 分类列表 | 否 |
| GET | `/api/v1/tags` | 标签列表 | 否 |

## 测试

```bash
pytest
```

测试全部基于 SQLite 内存库(aiosqlite),无需真实 MySQL:

| 层 | 测试文件 | 方式 |
|---|---|---|
| Service 层 | `tests/test_user_service.py` `tests/test_post_service.py` | 直接构造 Repository + Service,验证业务规则 |
| API 层 | `tests/test_api.py` | httpx + `dependency_overrides` 替换 `get_db_session`,覆盖完整请求链路 |

## CI

项目自带 GitHub Actions(`.github/workflows/ci.yml`):push / PR 时自动跑 `ruff check` + 全量测试(Python 3.11 / 3.12 矩阵)。

## 贡献

欢迎提 Issue 和 PR,参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 目录约定

- **`base/` 目录**:只放 `Protocol` 接口,纯结构化子类型,不依赖任何具体实现
- **`impl/` 目录**:放具体实现,依赖 SQLAlchemy/Pydantic 等基础设施
- **新增业务**:在 `domain/entities/` 加 ORM → 在 `repository/base/` 加接口 → 在 `repository/impl/` 加实现 → 在 `service/` 同理 → 在 `api/v1/` 加路由 → 最后在 `containers.py` 注册

## License

MIT