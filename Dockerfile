# Multi-stage build: a "builder" stage installs dependencies into a venv,
# and the final runtime stage copies only that venv + app code, keeping the
# shipped image free of build tooling (gcc, headers) that psycopg2/bcrypt
# need at install time but not at runtime.

FROM python:3.12-slim AS builder

# psycopg2-binary and bcrypt install pure-C extensions; build-essential +
# libpq-dev provide the compiler/headers needed during `pip install`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only dependency metadata first so Docker's layer cache is reused
# across builds unless dependencies actually change.
COPY pyproject.toml ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Install the project's runtime deps (pyproject has no build backend for
# packaging the app itself — we just need the dependency list installed).
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir fastapi "uvicorn[standard]" sqlalchemy alembic \
       pydantic pydantic-settings "python-jose[cryptography]" "passlib[bcrypt]" \
       "bcrypt<4.0.0" psycopg2-binary python-multipart


FROM python:3.12-slim AS runtime

# libpq5 is the runtime-only counterpart of libpq-dev (no compiler needed).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1

WORKDIR /app
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
