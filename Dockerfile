# ============ 构建阶段 ============
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# 先装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 装依赖到独立目录,便于拷贝到运行时镜像
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "sqlalchemy[asyncio]>=2.0.36" \
    "aiomysql>=0.2.0" \
    "pymysql>=1.1.1" \
    "alembic>=1.14.0" \
    "dependency-injector>=4.41.0" \
    "pydantic>=2.10.0" \
    "pydantic-settings>=2.7.0" \
    "bcrypt>=4.1.0" \
    "python-jose[cryptography]>=3.3.0" \
    "python-multipart>=0.0.20" \
    "email-validator>=2.2.0"

# ============ 运行时阶段 ============
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# 运行时只需要 mysql 客户端(给 alembic 用)和 curl(健康检查)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 拷贝依赖
COPY --from=builder /install /usr/local

WORKDIR /app

# 拷贝源码
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY pyproject.toml /app/pyproject.toml

# 非 root 用户运行
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]