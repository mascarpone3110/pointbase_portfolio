# --------------------------
# 1. Build stage
# --------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# OS パッケージ（PostgreSQL, psycopg2, Pillow などで必要）
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    musl-dev \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# --------------------------
# 2. Runtime stage
# --------------------------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ランタイム必要パッケージだけ
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Gunicorn 起動 (Fargate 用)
CMD ["gunicorn", "crowdfund_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
