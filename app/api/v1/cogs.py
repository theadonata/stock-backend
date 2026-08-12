"""cogs_components CRUD — per-period HPP inputs."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.cogs_component import CogsComponent
from app.schemas.cogs import CogsComponentCreate, CogsComponentRead, CogsComponentUpdate

router = APIRouter(prefix="/cogs-components", tags=["cogs"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CogsComponentRead])
def list_cogs_components(db: Session = Depends(get_db)) -> list[CogsComponent]:
    return db.query(CogsComponent).order_by(CogsComponent.period.desc()).all()


@router.post("", response_model=CogsComponentRead, status_code=status.HTTP_201_CREATED)
def create_cogs_component(payload: CogsComponentCreate, db: Session = Depends(get_db)) -> CogsComponent:
    component = CogsComponent(**payload.model_dump())
    db.add(component)
    try:
        db.commit()
    except IntegrityError as exc:
        # Most likely cause: the unique constraint on `period` — a breakdown
        # for that month already exists.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"COGS components for period {payload.period} already exist",
        ) from exc
    db.refresh(component)
    return component


def _get_component_or_404(db: Session, component_id: int) -> CogsComponent:
    component = db.query(CogsComponent).filter(CogsComponent.id == component_id).first()
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COGS component not found")
    return component


@router.get("/{component_id}", response_model=CogsComponentRead)
def get_cogs_component(component_id: int, db: Session = Depends(get_db)) -> CogsComponent:
    return _get_component_or_404(db, component_id)


@router.patch("/{component_id}", response_model=CogsComponentRead)
def update_cogs_component(
    component_id: int, payload: CogsComponentUpdate, db: Session = Depends(get_db)
) -> CogsComponent:
    component = _get_component_or_404(db, component_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(component, field, value)
    db.commit()
    db.refresh(component)
    return component


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cogs_component(component_id: int, db: Session = Depends(get_db)) -> None:
    component = _get_component_or_404(db, component_id)
    db.delete(component)
    db.commit()
