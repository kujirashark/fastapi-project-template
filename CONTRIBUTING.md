# 贡献指南

感谢关注本项目!欢迎提交 Issue 和 Pull Request。

## 开发环境

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装依赖(含开发依赖)
pip install -e ".[dev]"

# 3. 启动本地 MySQL(或修改 .env 中的 DB_HOST)
docker run -d --name blog-mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root_pass \
  -e MYSQL_DATABASE=blog \
  -e MYSQL_USER=blog \
  -e MYSQL_PASSWORD=blog_pass \
  mysql:8.0

# 4. 初始化数据库
alembic upgrade head
```

## 本地检查

提交前请确保以下命令全部通过:

```bash
# 代码风格检查
ruff check src tests

# 自动修复可修复的问题
ruff check --fix src tests

# 运行测试
pytest
```

## 新增业务的步骤

参考 README 的「目录约定」一节:

1. `domain/entities/` 加 ORM 实体 → `domain/schemas/` 加 DTO
2. `repository/base/` 加 Protocol 接口 → `repository/impl/` 加 SQLAlchemy 实现
3. `service/base/` 加 Protocol 接口 → `service/impl/` 加业务实现
4. `api/v1/` 加路由,`api/v1/router.py` 注册
5. `containers.py` 注册 Provider
6. 为 Service 层写单元测试,为 API 层写集成测试(参考 `tests/test_api.py`)

## 提交规范

- 遵循现有代码风格(4 空格缩进,行宽 100)
- 每个 PR 聚焦一件事,附带必要说明
- 新功能必须带测试
