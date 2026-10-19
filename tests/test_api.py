"""API 层集成测试。

展示最佳实践:通过 FastAPI 的 dependency_overrides 替换 get_db_session,
把真实 MySQL 换成 SQLite 内存库,从而在不启动数据库的情况下测完整请求链路
(路由 → DI 容器 → Service → Repository → DB)。
"""

from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.main import app


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """用测试 session 覆盖 get_db_session,返回异步 HTTP 客户端。"""

    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        yield db_session
        await db_session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_login_me_flow(api_client: Any):
    """注册 → 登录 → 带 token 访问 /users/me 的完整链路。"""
    # 注册
    resp = await api_client.post(
        "/api/v1/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "carol"

    # 登录拿 token
    resp = await api_client.post(
        "/api/v1/auth/login",
        json={"username": "carol", "password": "secret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # 携带 token 获取当前用户
    resp = await api_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "carol@example.com"


@pytest.mark.asyncio
async def test_unauthorized_access(api_client: Any):
    """无 token 访问受保护接口应返回 401。"""
    resp = await api_client.get("/api/v1/users/me")
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"]["code"] == "authentication_error"


@pytest.mark.asyncio
async def test_post_crud_flow(api_client: Any):
    """创建文章 → 列表 → 详情 → 更新 → 删除的完整链路。"""
    # 注册 + 登录
    await api_client.post(
        "/api/v1/auth/register",
        json={"username": "dave", "email": "dave@example.com", "password": "secret123"},
    )
    resp = await api_client.post(
        "/api/v1/auth/login",
        json={"username": "dave", "password": "secret123"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 创建文章
    resp = await api_client.post(
        "/api/v1/posts",
        json={"title": "My First Post", "content": "Hello World"},
        headers=headers,
    )
    assert resp.status_code == 201
    post_id = resp.json()["id"]

    # 未登录创建应 401
    resp = await api_client.post("/api/v1/posts", json={"title": "x", "content": "y"})
    assert resp.status_code == 401

    # 列表(公开)
    resp = await api_client.get("/api/v1/posts", params={"keyword": "First"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["page_info"]["total"] == 1
    assert body["items"][0]["title"] == "My First Post"

    # 详情
    resp = await api_client.get(f"/api/v1/posts/{post_id}")
    assert resp.status_code == 200

    # 更新(作者本人)
    resp = await api_client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"

    # 删除
    resp = await api_client.delete(f"/api/v1/posts/{post_id}", headers=headers)
    assert resp.status_code == 204

    # 详情应 404
    resp = await api_client.get(f"/api/v1/posts/{post_id}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"
