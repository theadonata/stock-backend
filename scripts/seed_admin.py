"""
Seed a single placeholder admin user so there's a way to log in on a fresh
database. Run once after migrations, e.g.:

    docker compose exec app python -m scripts.seed_admin

PLACEHOLDER CREDENTIALS (change immediately after first login in anything
beyond local dev — this script is idempotent and safe to re-run, it just
skips creating the user if it already exists):
    username: value of SEED_ADMIN_USERNAME env var, default "admin"
    password: value of SEED_ADMIN_PASSWORD env var, default "changeme123"

There is intentionally no public self-registration endpoint (per spec) —
this script is the only way new accounts get created for now.
"""
import os

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "changeme123"


def seed_admin() -> None:
    username = os.environ.get("SEED_ADMIN_USERNAME", DEFAULT_USERNAME)
    password = os.environ.get("SEED_ADMIN_PASSWORD", DEFAULT_PASSWORD)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing is not None:
            print(f"User '{username}' already exists — skipping seed.")
            return

        user = User(username=username, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        print(f"Seeded placeholder admin user '{username}'. Change this password after first login.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
