# Import all ORM models here so that Alembic's autogenerate (and
# Base.metadata.create_all, used only in tests) can discover every table
# by simply importing this package.
from app.models.user import User  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.inventory_ledger import InventoryLedger, MovementDirection  # noqa: F401
from app.models.sale import Sale  # noqa: F401
from app.models.expense import Expense  # noqa: F401
from app.models.cogs_component import CogsComponent  # noqa: F401
