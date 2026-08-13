"""Sales CRUD, with the same future-dated-entry business rule as inventory
movements (per spec's error-handling section)."""
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleRead, SaleUpdate

router = APIRouter(prefix="/sales", tags=["sales"], dependencies=[Depends(get_current_user)])


def _reject_future_date(entry_date: date) -> None:
    if entry_date > datetime.now(UTC).date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date cannot be in the future")


@router.get("", response_model=list[SaleRead])
def list_sales(db: Session = Depends(get_db)) -> list[Sale]:
    return db.query(Sale).order_by(Sale.date.desc()).all()


@router.post("", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)) -> Sale:
    _reject_future_date(payload.date)
    sale = Sale(**payload.model_dump())
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def _get_sale_or_404(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(sale_id: int, db: Session = Depends(get_db)) -> Sale:
    return _get_sale_or_404(db, sale_id)


@router.patch("/{sale_id}", response_model=SaleRead)
def update_sale(sale_id: int, payload: SaleUpdate, db: Session = Depends(get_db)) -> Sale:
    sale = _get_sale_or_404(db, sale_id)
    updates = payload.model_dump(exclude_unset=True)
    if "date" in updates and updates["date"] is not None:
        _reject_future_date(updates["date"])
    for field, value in updates.items():
        setattr(sale, field, value)
    db.commit()
    db.refresh(sale)
    return sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)) -> None:
    sale = _get_sale_or_404(db, sale_id)
    db.delete(sale)
    db.commit()
