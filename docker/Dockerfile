FROM docker.io/library/python:3.13-slim@sha256:56ab277ddf459858f94052252565945c34617c841818faf8f34f6896de06cffe AS base

ENV PATH="/venv/bin:$PATH" \
    VIRTUAL_ENV="/venv" \
    APP_HOME="/home/app"

RUN set -eux; apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS build

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT="/venv"

COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /usr/local/bin/
RUN set -eux; apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv /venv
WORKDIR $APP_HOME

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv build --wheel && \
    uv pip install --no-deps dist/*.whl

FROM base

RUN useradd --system --no-create-home nonroot

COPY --from=build /venv /venv
COPY --from=build /home/app/src /home/app/src

WORKDIR /home/app

USER nonroot
