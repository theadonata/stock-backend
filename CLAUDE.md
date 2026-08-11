# CLAUDE.md

This is the **backend** repo for the Stock/HPP business-finance project.

## Project status

No stack has been chosen yet and no application code exists. Don't assume a
language, framework, or data store — ask the user before scaffolding
anything.

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
