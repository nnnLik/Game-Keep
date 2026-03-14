ARG PYTHON_IMAGE=python:3.14-slim

FROM $PYTHON_IMAGE AS base

ENV PYTHONUNBUFFERED=1 \
	PYSETUP_PATH="/opt/pysetup" \
	VENV_PATH="/opt/pysetup/.venv" \
	APP_PATH="/opt/app" \
	PYTHONPATH="/opt/app/src"

RUN apt-get update && \
	pip install uv==0.9.2 && \
	rm -rf /var/lib/apt/lists/*

WORKDIR $PYSETUP_PATH

FROM base AS builder

COPY pyproject.toml uv.lock $PYSETUP_PATH/
RUN uv sync --group=prod
ENV PATH="$VENV_PATH/bin:$PATH"

FROM builder AS dev

RUN uv sync --group=dev
COPY . ${APP_PATH}
WORKDIR ${APP_PATH}

FROM $PYTHON_IMAGE AS prod

ENV PYTHONUNBUFFERED=1 \
	VENV_PATH="/opt/venv" \
	APP_PATH="/opt/app" \
	PYTHONPATH="/opt/app/src" \
	PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/pysetup/.venv $VENV_PATH
COPY . ${APP_PATH}
WORKDIR ${APP_PATH}
