# initdb scripts

`.sql` or `.sh` files placed here run once, in filename order, the first
time the Postgres data directory is initialized (empty volume). Nothing is
required today — alembic (`app`) owns all schema/table creation — so this
directory is currently empty. Use it only for things that must exist
*before* alembic runs, e.g. a `CREATE EXTENSION` statement:

```sql
-- 001-extensions.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Do not put credentials, seed data, or anything env-specific here — this
image is meant to be built once and reused across environments.
