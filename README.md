# stock-backend

API, business logic, and data layer for the Stock/HPP business-finance app —
a small internal tool that replaces an Excel-based tracker
(`Catatan_HPP_Keuangan_Bisnis.xlsx`) for a small bags/accessories business.
It tracks products, inventory movements, sales, operational expenses, and
COGS (HPP) inputs, and computes Laba Rugi (profit & loss) on demand for any
month.

Part of the `stock-*` multi-repo project. See `CLAUDE.md` for scope and
sibling-repo relationships.

## Tech stack

- **FastAPI** — REST API, versioned under `/api/v1`, with OpenAPI docs
  auto-generated at `/docs` (the API contract for `stock-frontend` /
  `stock-qa`).
- **PostgreSQL** + **SQLAlchemy** (ORM) + **Alembic** (migrations).
- **JWT auth** (python-jose) with **bcrypt** password hashing (passlib) —
  single role tier, every authenticated user can read/write.
- **pytest** + **httpx** for tests.
- Packaged as a **multi-stage Docker image**; local dev runs via
  **docker-compose** (app + Postgres).

## Data model

- `users` — auth only (username, hashed password).
- `products` — catalog: name, unit, purchase price per unit.
- `inventory_ledger` — one row per stock movement (in/out). Current stock
  and historical snapshots are both *derived* by summing this ledger —
  there is no stored "current stock" column, so stock can never silently
  drift from its audit trail.
- `sales` — revenue entries (source/product, date, amount).
- `expenses` — operational cost entries (category, date, amount).
- `cogs_components` — per-month HPP inputs (persediaan awal/akhir,
  pembelian bahan baku, ongkos kirim, biaya tenaga kerja, overhead, kemasan).
- **Laba Rugi (P&L) is not a stored table.** `GET /api/v1/reports/pnl` computes
  it on the fly from sales + cogs_components + expenses for a given period.

`products`, `sales`, `expenses`, and `cogs_components` all support full CRUD
(list/create/get/update/delete). `inventory_ledger` is deliberately
**append-only** — create and list only, no update/delete — since it's an
audit trail; editing a past movement would let recorded stock silently
drift from reality, which the ledger design exists to prevent.

## Running locally via Docker

Prerequisites: Docker + Docker Compose.

1. **Start the stack** (builds the app image, starts Postgres, runs
   migrations, then starts the API):

   ```bash
   docker compose up --build
   ```

   This uses `docker-compose.yml`, which reads config from `.env.local`
   (gitignored, never committed — see that file for what each variable
   does and edit the placeholder values there directly; there is no
   separate `.env.example` to copy from).

   Postgres runs as `stock_hpp_postgres` (db `stock_hpp_db`, volume
   `stock_hpp_pgdata`) — named distinctively so it won't collide with other
   local projects' `postgres`/`db` containers.

2. **Migrations** run automatically as part of `docker compose up` (see the
   `command:` in `docker-compose.yml`). To run them manually instead:

   ```bash
   docker compose exec stock_hpp_app alembic upgrade head
   ```

3. **Seed the placeholder admin login** (one-time, after migrations):

   ```bash
   docker compose exec stock_hpp_app python -m scripts.seed_admin
   ```

   This creates a single admin user for logging in on a fresh database.
   Credentials come from `SEED_ADMIN_USERNAME` / `SEED_ADMIN_PASSWORD` env
   vars, defaulting to **username `admin`, password `changeme123`** — see
   `scripts/seed_admin.py`. There is no public self-registration endpoint;
   this script is the only way accounts get created. Change this password
   (or provision a real account and stop using this one) before any real
   deployment.

4. **API docs**: once running, the app is at `http://localhost:8000`, with
   interactive OpenAPI docs at **`http://localhost:8000/docs`**. Use the
   "Authorize" button there with a bearer token obtained from
   `POST /api/v1/auth/login`.

5. **Health check**: `GET http://localhost:8000/healthz`.

## Running tests

Tests use an in-memory SQLite DB (no Postgres/Docker required) and focus on
the business logic most likely to be subtly wrong: running stock balance
from the ledger, the COGS formula, and P&L aggregation across periods.

Outside Docker, with a local Python 3.12 environment:

```bash
pip install -e ".[dev]"
pytest
```

Or inside the built image:

```bash
docker compose run --rm stock_hpp_app pip install -e ".[dev]" && pytest
```

## Project layout

```
app/
  main.py            FastAPI app + router registration
  core/               config (pydantic-settings) + security (hashing/JWT)
  db/                 SQLAlchemy engine/session setup
  models/             SQLAlchemy ORM models
  schemas/            Pydantic request/response models
  api/v1/              routers (auth, products, inventory, sales, expenses, cogs, reports)
  services/            business logic (auth, inventory ledger math, P&L)
alembic/               migrations
scripts/seed_admin.py  one-time placeholder admin seed
tests/                 pytest suite
```
