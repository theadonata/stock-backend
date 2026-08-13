# Standalone Postgres image for stock-backend, versioned and built
# separately from the app so it can be deployed as its own k8s workload
# (StatefulSet) instead of being tied to the app's release cycle.
#
# Credentials are NOT baked in here — POSTGRES_USER/PASSWORD/DB are still
# supplied at runtime (via k8s Secret / docker-compose env), matching the
# base postgres image's own convention. Only schema-bootstrap scripts that
# are safe to be public belong in initdb/.

FROM postgres:16-alpine

# The base image tag is floating and its last rebuild can lag behind
# Alpine's own package patches (same reasoning as stock-frontend's nginx
# stage), so pull in current package versions at build time.
RUN apk update && apk upgrade --no-cache

# gosu exists solely so the entrypoint can start as root (to fix directory
# ownership) and then drop to the "postgres" user before running the actual
# server. Running as "postgres" from the start skips that step entirely --
# the entrypoint only execs gosu when id -u = 0 -- so the binary is dead
# weight here, and it's the one part of this image apk upgrade can't patch
# (it's a statically-linked Go binary, not an apk package; upstream's own
# latest gosu release still ships the same vulnerable Go stdlib build).
RUN rm -f /usr/local/bin/gosu

# Anything in /docker-entrypoint-initdb.d/ is run once, in filename order,
# only when the data directory is empty (first container start). Use this
# for extensions/roles/schemas that must exist before the app's alembic
# migrations run — not for data.
COPY initdb/ /docker-entrypoint-initdb.d/

# The base image's PGDATA is already owned by postgres:postgres, so running
# as that user from the start (uid 70 in this alpine image) needs no root
# step -- named volumes inherit an image directory's ownership on first
# mount, so this works with docker-compose's stock_hpp_pgdata volume too.
USER postgres

HEALTHCHECK --interval=5s --timeout=5s --retries=10 \
  CMD pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
