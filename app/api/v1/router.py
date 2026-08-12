"""Aggregates all v1 routers into one, mounted once in app.main."""
from fastapi import APIRouter

from app.api.v1 import auth, cogs, expenses, inventory, products, reports, sales

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(sales.router)
api_router.include_router(expenses.router)
api_router.include_router(cogs.router)
api_router.include_router(reports.router)
