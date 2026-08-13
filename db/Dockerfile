# Standalone Postgres image for stock-backend, versioned and built
# separately from the app so it can be deployed as its own k8s workload
# (StatefulSet) instead of being tied to the app's release cycle.
#
# Credentials are NOT baked in here — POSTGRES_USER/PASSWORD/DB are still
# supplied at runtime (via k8s Secret / docker-compose env), matching the
# base postgres image's own convention. Only schema-bootstrap scripts that
# are safe to be public belong in initdb/.

FROM postgres:16-alpine

# Anything in /docker-entrypoint-initdb.d/ is run once, in filename order,
# only when the data directory is empty (first container start). Use this
# for extensions/roles/schemas that must exist before the app's alembic
# migrations run — not for data.
COPY initdb/ /docker-entrypoint-initdb.d/

HEALTHCHECK --interval=5s --timeout=5s --retries=10 \
  CMD pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
