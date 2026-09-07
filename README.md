# stock-backend

> The API and database behind a small business's sales & inventory tracker.

## About the project

A small bags & accessories business used to track everything — sales,
stock, expenses, and cost of goods sold — in a single Excel file
(`Catatan_HPP_Keuangan_Bisnis.xlsx`). **Stock/HPP** ("HPP" is Indonesian
for *Harga Pokok Penjualan*, i.e. Cost of Goods Sold) replaces that
spreadsheet with a proper web app.

**This repo is the engine room.** It's the REST API and database that
store every product, sale, stock movement, and expense, and that compute
profit & loss (Laba Rugi) on demand. The web page people actually click
around in lives in a separate repo, [stock-frontend](https://github.com/theadonata/stock-frontend) — it talks to this API over HTTP and never touches this repo's code or database directly.

### Part of a bigger project

Stock/HPP is split into six repos, each one buildable and deployable on
its own:

| Repo | What it does |
|---|---|
| [stock-frontend](https://github.com/theadonata/stock-frontend) | The web app people use day to day |
| **stock-backend** (this repo) | The API and database — stores data, does the math |
| [stock-infrastructure](https://github.com/theadonata/stock-infrastructure) | Deploys and runs everything on a server |
| [stock-qa](https://github.com/theadonata/stock-qa) | Automated tests that check everything works |
| [stock-business-analyst](https://github.com/theadonata/stock-business-analyst) | The original business requirements this is built from |
| [stock-platform](https://github.com/theadonata/stock-platform) | An internal dashboard for the team building this project |

## What it tracks

- **Products** — name, unit, purchase price
- **Inventory movements** — every stock-in / stock-out event. Current
  stock is always calculated from this history, never stored as its own
  number — so it can never quietly drift from reality.
- **Sales** and **expenses** — simple dated entries
- **COGS inputs** — the monthly numbers (opening/closing stock, materials
  purchased, shipping, labor, overhead, packaging) that feed into...
- **Profit & Loss** — not stored anywhere; calculated fresh every time you
  ask for it, for whatever month/period you pick

Everything above supports the usual create/read/update/delete operations
*except* inventory movements, which are append-only on purpose — it's an
audit trail, so past entries can't be edited or deleted.

## Built with

- [FastAPI](https://fastapi.tiangolo.com/) — the web framework, with
  interactive API docs generated automatically
- [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy](https://www.sqlalchemy.org/) (database + ORM) + [Alembic](https://alembic.sqlalchemy.org/) (migrations)
- JWT-based login (one shared role for now — anyone logged in can read/write)
- [pytest](https://docs.pytest.org/) for tests
- Docker + Docker Compose for local development

## Getting started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose

### Running it

```bash
docker compose up --build
```

This builds the app, starts a Postgres database, runs database migrations,
then starts the API — all in one command. Configuration comes from
`.env.local` (already in the repo, gitignored — open it and edit values
directly, there's no separate example file to copy from).

Once it's running:

- The API is at **http://localhost:8000**
- Interactive docs (try out every endpoint from your browser) are at
  **http://localhost:8000/docs**
- A basic health check is at **http://localhost:8000/healthz**

There's no public sign-up — create the one seed admin account after your
first migration:

```bash
docker compose exec stock_hpp_app python -m scripts.seed_admin
```

Defaults to username `admin`, password `changeme123` (configurable via
`SEED_ADMIN_USERNAME`/`SEED_ADMIN_PASSWORD`) — change this before any real
deployment.

## Running tests

Tests run against an in-memory database, so you don't need Postgres or
Docker for this:

```bash
pip install -e ".[dev]"
pytest
```

## Project structure

```
app/
  main.py       FastAPI app + router registration
  core/         configuration + password hashing/JWT
  db/           database connection setup
  models/       database tables (SQLAlchemy)
  schemas/      request/response shapes (Pydantic)
  api/v1/       one file per group of endpoints
  services/     the actual business logic (stock math, P&L calculation)
alembic/        database migrations
scripts/        one-off scripts (e.g. seeding the admin account)
tests/          the test suite
```
