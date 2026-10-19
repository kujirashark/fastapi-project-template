# FastAPI 分层架构最佳实践模板

> 一句话说清楚:这是一个 **FastAPI + Dependency-Injector 依赖注入** 的多用户博客示例项目,演示如何在真实项目中做到 **业务逻辑与框架解耦、每层只依赖接口不依赖实现**。克隆下来就能跑,换成你自己的业务就能用。

## 这个项目解决什么问题?

写 FastAPI 项目最常见的两个坑:

1. **所有代码堆在一起** —— 路由、数据库操作、业务规则混着写,越写越乱
2. **Service 直接 import 别的 Service / 到处传 SQLAlchemy 对象** —— 想写测试、想换数据库,牵一发动全身

本项目的答案是 **分层 + 依赖注入**:

```
你的请求 ──▶ api 层(收发 HTTP)──▶ service 层(业务规则)──▶ repository 层(读写数据库)──▶ MySQL
                    │                     │                      │
                    └────────────── 只依赖 Protocol 接口,不依赖具体实现 ──────────────┘
                                        ▲
                              DI 容器负责"组装"所有对象
```

- **换数据库?** 只改 `repository/impl/`,其他层一行不动
- **写单元测试?** 传个 Mock 实现进去就行,不用连数据库
- **新同事接手?** 看目录就知道代码该放哪

## 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| Web 框架 | FastAPI | 0.115+ |
| 依赖注入 | dependency-injector | 4.41+ |
| ORM | SQLAlchemy(全异步) | 2.0+ |
| 数据库 | MySQL | 8.0(驱动 aiomysql) |
| 数据迁移 | Alembic | 1.14+ |
| 鉴权 | JWT(python-jose)+ bcrypt 密码哈希 | — |
| 配置 | pydantic-settings(环境变量 / .env) | 2.7+ |
| 测试 | pytest + httpx(SQLite 内存库,不需要 MySQL) | — |
| 容器化 | Docker + docker-compose | — |

## 分层架构总览

```
src/app/
├── main.py                  # 应用入口:创建 FastAPI、装配 DI 容器、注册路由和异常处理
├── containers.py            # DI 容器:所有 Repository / Service 在这里"组装"
│
├── core/                    # 横切关注点(和业务无关的基础设施)
│   ├── config.py            #   配置:从 .env 读取,pydantic-settings 校验
│   ├── database.py          #   数据库:异步 engine + session 工厂
│   ├── security.py          #   安全:bcrypt 密码哈希 + JWT 签发/校验
│   └── exceptions.py        #   业务异常:NotFoundError / ConflictError / ...
│
├── domain/                  # 领域层:定义"数据长什么样",被所有层依赖
│   ├── entities/            #   SQLAlchemy ORM 实体(User / Post / Category / Tag)
│   └── schemas/             #   Pydantic 模型(请求体 / 响应体 / 分页)
│
├── repository/              # 仓储层:只管数据库读写,不含业务规则
│   ├── base/                #   Protocol 接口(长什么样)
│   └── impl/                #   SQLAlchemy 实现(具体怎么干)
│
├── service/                 # 业务逻辑层:领域规则都在这,不碰 HTTP 也不写 SQL
│   ├── base/                #   Protocol 接口
│   └── impl/                #   业务实现
│
└── api/                     # 路由层:FastAPI Router + Depends,薄薄一层
    ├── deps.py              #   依赖注入工厂:session / service / 当前登录用户
    ├── errors.py            #   全局异常处理:业务异常 → 统一 JSON 错误格式
    └── v1/                  #   具体路由:auth / users / posts / categories / tags
```

**铁律:依赖方向只能自上而下** `api → service → repository → domain`,通过 DI 容器装配,任何一层都不直接 import 下一层的**实现类**,只 import `base/` 里的 **Protocol 接口**。

## 一个请求的完整旅程(以"创建文章"为例)

```
① 客户端发起请求
   POST /api/v1/posts   Authorization: Bearer <JWT>
   Body: {"title": "Hello", "content": "...", "category_id": 1, "tag_ids": [1]}

        │
        ▼
② api/v1/posts.py —— 只做三件事:解析参数、拿依赖、调 service
   async def create_post(
       data: PostCreate,                      # ← Pydantic 自动校验请求体
       current_user: CurrentUser,             # ← deps.py 从 JWT 解析出当前用户
       post_service: PostServiceDep,          # ← deps.py 从 DI 容器拿 service
   ):
       post = await post_service.create(data, author_id=current_user.id)

        │
        ▼
③ service/impl/post_service.py —— 业务规则集中地
   async def create(self, data, author_id):
       作者存在吗?   → user_repository.get(author_id)      不存在 → 404
       分类存在吗?   → category_repository.get(...)        不存在 → 404
       标签都存在吗? → tag_repository.get_many_by_ids(...) 缺失  → 422
       全部通过 → 组装 Post 实体 → 交给仓储层保存

        │
        ▼
④ repository/impl/post_repository.py —— 只管持久化,不问为什么
   session.add(post) + flush → INSERT INTO posts ...

        │
        ▼
⑤ 事务提交:请求成功后 api/deps.py 的 get_db_session 统一 commit;抛异常则 rollback

        │
        ▼
⑥ 响应:PostOut(Pydantic 模型)自动序列化 → 201 Created
```

**关键点:api 层从不 `import PostService`,所有依赖都通过 `api/deps.py` 的 Depends 工厂从容器获取。**

## 核心设计(三个值得抄走的模式)

### 模式 1:Protocol 接口 + DI 容器装配

每层的 `base/` 只放 `Protocol` 接口(纯声明、零实现):

```python
# repository/base/user.py
class IUserRepository(IBaseRepository[User, int], Protocol):
    async def get_by_email(self, email: str) -> User | None: ...
```

实现类放在 `impl/`,**同时继承接口和 SQLAlchemy 基类**:

```python
# repository/impl/user_repository.py
class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], IUserRepository):
    model = User
```

最后在 `containers.py` 把接口和实现"焊"在一起:

```python
# containers.py
class Container(containers.DeclarativeContainer):
    db_session = providers.Dependency(instance_of=AsyncSession)  # 请求级 session

    user_repository = providers.Factory(SQLAlchemyUserRepository, session=db_session)
    user_service    = providers.Factory(UserService, user_repository=user_repository)
```

> **为什么值得?** 测试时把 Factory 指向 Mock 类即可,业务代码一行不改;想换数据库就只写一个新 impl。

### 模式 2:通用 Repository 基类,少写 80% 的 CRUD

`IBaseRepository[T, ID]` 定义了 `get / list / count / add / delete / flush` 六个通用方法;`SQLAlchemyBaseRepository[T]` 是它的通用实现。新实体的仓储只需继承并指定 `model`:

```python
class SQLAlchemyCategoryRepository(SQLAlchemyBaseRepository[Category], ICategoryRepository):
    model = Category   # 通用 CRUD 白拿,只写 Category 特有的方法
```

### 模式 3:事务边界统一在 API 层

- `api/deps.py` 的 `get_db_session`:每个请求开一个新 `AsyncSession`,请求成功 `commit`、抛异常 `rollback`
- Service / Repository 只管 `flush`(拿到数据库生成的 id 等),**从不自己 commit**
- 好处:一次请求涉及多张表的写入时,要么全成功要么全回滚,业务代码不用操心事务

## 如何新增一个业务?(检查清单)

假设要加一个"评论(Comment)"功能,按顺序走:

- [ ] 1. `domain/entities/comment.py` —— 加 ORM 实体(记得加入 `alembic/env.py` 的 import)
- [ ] 2. `domain/schemas/comment.py` —— 加 `CommentCreate / CommentUpdate / CommentOut`
- [ ] 3. `repository/base/comment.py` —— 加 `ICommentRepository(Protocol)`
- [ ] 4. `repository/impl/comment_repository.py` —— 加 SQLAlchemy 实现
- [ ] 5. `service/base/comment.py` —— 加 `ICommentService(Protocol)`
- [ ] 6. `service/impl/comment_service.py` —— 加业务实现(校验规则写这里)
- [ ] 7. `api/v1/comments.py` —— 加路由,并在 `api/v1/router.py` 注册
- [ ] 8. `containers.py` —— 注册 `comment_repository` 和 `comment_service`
- [ ] 9. `alembic revision --autogenerate -m "add comment"` → `alembic upgrade head`
- [ ] 10. 写测试:Service 层单测 + API 层集成测试(照抄 `tests/` 里的例子)

## 快速开始

### 方式一:Docker(推荐,一条命令跑通)

```bash
# 1. 复制环境变量文件(首次)
cp .env.example .env

# 2. 一键启动:自动起 MySQL + 跑数据库迁移 + 启动应用
docker-compose up --build
```

启动后访问:

- Swagger 文档:http://localhost:8000/docs
- ReDoc 文档:http://localhost:8000/redoc
- 健康检查:http://localhost:8000/health

### 方式二:本地开发

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 安装依赖(含 dev 工具链:pytest / ruff / httpx)
pip install -e ".[dev]"

# 3. 准备一个 MySQL,并修改 .env 里的 DB_HOST / DB_USER / DB_PASSWORD
#    (最快的方式:docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root_pass mysql:8.0)

# 4. 执行数据库迁移
alembic upgrade head

# 5. 启动服务
uvicorn app.main:app --reload --app-dir src
```

## 业务实体

| 实体 | 说明 | 关系 |
|---|---|---|
| `User` | 多用户,bcrypt 哈希密码,登录返回 JWT | 1 个作者 → N 篇文章 |
| `Post` | 文章(标题/摘要/内容) | 关联 author、category、tags |
| `Category` | 分类 | 1 个分类 → N 篇文章 |
| `Tag` | 标签 | N ↔ N 多对多关联文章 |

## API 路由速查

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | `/api/v1/auth/register` | 注册 | ❌ |
| POST | `/api/v1/auth/login` | 登录(用户名或邮箱),返回 JWT | ❌ |
| GET | `/api/v1/users/me` | 获取当前用户 | ✅ |
| PUT | `/api/v1/users/me` | 更新当前用户资料 | ✅ |
| DELETE | `/api/v1/users/me` | 注销当前用户 | ✅ |
| GET | `/api/v1/posts` | 文章列表(分页 + 关键词/作者/分类/标签筛选) | ❌ |
| POST | `/api/v1/posts` | 创建文章 | ✅ |
| GET | `/api/v1/posts/{id}` | 文章详情 | ❌ |
| PUT | `/api/v1/posts/{id}` | 更新文章(仅作者本人) | ✅ |
| DELETE | `/api/v1/posts/{id}` | 删除文章(仅作者本人) | ✅ |
| GET | `/api/v1/categories` | 分类列表 | ❌ |
| POST | `/api/v1/categories` | 创建分类 | ✅ |
| DELETE | `/api/v1/categories/{id}` | 删除分类 | ✅ |
| GET | `/api/v1/tags` | 标签列表 | ❌ |
| POST | `/api/v1/tags` | 创建标签 | ✅ |
| DELETE | `/api/v1/tags/{id}` | 删除标签 | ✅ |

**统一错误格式**(所有业务异常都返回这个结构,见 `api/errors.py`):

```json
{
  "error": {
    "code": "not_found",
    "message": "文章 9999 不存在",
    "details": {}
  }
}
```

## 测试

测试全部基于 **SQLite 内存库**,不需要启动 MySQL:

```bash
pytest
```

| 层 | 文件 | 测什么 |
|---|---|---|
| Service 层(单元测试) | `tests/test_user_service.py`、`tests/test_post_service.py` | 业务规则:重名拒绝、密码校验、权限校验、分页等 |
| API 层(集成测试) | `tests/test_api.py` | 完整请求链路:路由 → DI → Service → Repository → DB |

API 测试的技巧值得一看:通过 FastAPI 的 `dependency_overrides` 把 `get_db_session` 换成测试 session,MySQL 就被"无缝替换"成了 SQLite——这正是接口解耦的收益。

## CI

`.github/workflows/ci.yml`:push / PR 时自动跑 `ruff check` + 全量测试(Python 3.11 / 3.12 矩阵)。

## 目录约定(团队协作必读)

- **`base/` 目录**:只放 `Protocol` 接口,不写任何实现
- **`impl/` 目录**:放具体实现,可以随便用 SQLAlchemy / Pydantic 等基础设施
- **新增业务**:严格按上面的「检查清单」走,别跳步
- **代码风格**:行宽 100,`ruff` 负责,CI 会卡

## 常见问题(FAQ)

**Q: 为什么用 Protocol 而不是 ABC(抽象基类)?**
Protocol 是结构化子类型,实现类不需要显式继承也能通过类型检查;当然本项目里实现类显式继承了接口,更直观。两者都行,选一种坚持用。

**Q: 为什么 Service 不直接操作 `AsyncSession`?**
事务边界统一在 API 层(`get_db_session`),Service 只通过 Repository 操作数据。这样 Service 可以脱离数据库单独测试。

**Q: 为什么请求结束才 commit,而不是每个 Repository 方法 commit?**
一个业务动作可能写多张表(如创建文章同时更新标签关联),中途 commit 会破坏原子性。

**Q: 想换 PostgreSQL 怎么办?**
改 `core/config.py` 的连接 URL(驱动换 asyncpg)+ `pyproject.toml` 依赖,repository 层代码基本不用动(本项目没有用 MySQL 方言特有写法)。

## 贡献

欢迎提 Issue 和 PR,参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT
