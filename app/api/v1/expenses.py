"""Expenses CRUD, same future-dated-entry rule as sales/inventory."""
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(get_current_user)])


def _reject_future_date(entry_date: date) -> None:
    if entry_date > datetime.now(UTC).date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date cannot be in the future")


@router.get("", response_model=list[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)) -> list[Expense]:
    return db.query(Expense).order_by(Expense.date.desc()).all()


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> Expense:
    _reject_future_date(payload.date)
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def _get_expense_or_404(db: Session, expense_id: int) -> Expense:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)) -> Expense:
    return _get_expense_or_404(db, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)) -> Expense:
    expense = _get_expense_or_404(db, expense_id)
    updates = payload.model_dump(exclude_unset=True)
    if "date" in updates and updates["date"] is not None:
        _reject_future_date(updates["date"])
    for field, value in updates.items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)) -> None:
    expense = _get_expense_or_404(db, expense_id)
    db.delete(expense)
    db.commit()
