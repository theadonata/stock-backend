# CLAUDE.md

This is the **backend** repo for the Stock/HPP business-finance project.

## Project status

Stack chosen: FastAPI + PostgreSQL + SQLAlchemy/Alembic. See
`stock-business-analyst/docs/superpowers/specs/2026-08-12-stack-architecture-design.md`
for the full design (data model, auth, error handling, testing strategy).

## Relationship to sibling repos

This project is split across independent repos, each buildable and
deployable on its own with no shared code or path dependency between them:

- `stock-frontend` — client-side UI
- `stock-backend` (this repo) — API / business logic / data layer
- `stock-infrastructure` — CI/CD, deployment, IaC
- `stock-qa` — test plans, test automation
- `stock-business-analyst` — requirements, specs, source material (incl. the original HPP/business-finance notes)

Contracts this repo exposes (API shapes, etc.) should be versioned/documented
so sibling repos never need to read this repo's source to consume them.

## Working here

`.claude/` config (agents, hooks, skills, MCP) is kept identical across all
five repos on purpose, so any agent persona works the same way regardless of
which repo it's invoked in. Once a stack is chosen, update this file with
real build/lint/test commands and architecture notes.

## Git

Do not commit changes in this repo automatically — even when using
atomic-commit or similar workflows. Only commit when the user explicitly
asks for it.

Never push directly to the `main` branch, even when explicitly asked to
"push" or "commit and push" — `main` is protected and requires a pull
request. Always push to a new branch and open a PR instead, across all
five `stock-*` repos.

## Code style

Always put comments in code so it is understandable by a human reader —
explain what non-obvious blocks (business logic, calculations, validation
rules) do, not just restate the syntax.

## Environment files

Always use `.env.local` for local config — never create or reintroduce a
`.env.example`/`.env.sample` template file. `.env.local` already exists in
this repo (gitignored) and holds the real placeholder values directly; if a
new env var is needed, add it straight to `.env.local` (with a comment
explaining it) rather than adding a separate example file for someone to
copy from.

## Gitignore

Always ensure a `.gitignore` exists in this repo — never let it be
deleted or skipped when scaffolding. It has two parts:

- A **shared baseline** kept identical (word-for-word) across all five
  `stock-*` repos: `.env`, `.env.local`, `.claude/settings.local.json`. If
  you add an entry to this shared baseline in any one repo, add the same
  line to the other four repos' `.gitignore` files too, so they stay in
  sync.
- **Repo-specific entries** below the baseline (e.g. `__pycache__/`,
  `.venv/` here; `node_modules`, `dist` in the frontend repos) — these are
  expected to differ per repo's tooling and should NOT be copied to
  siblings.
