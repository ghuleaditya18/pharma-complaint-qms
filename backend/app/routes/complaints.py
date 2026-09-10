from datetime import datetime
import logging
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Complaint
from app.schemas import ComplaintCreate, ComplaintResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Complaints"])


def _generate_complaint_id(db: Session) -> str:
    """Generate a unique sequential complaint identifier, e.g., CMP-2026-0001."""
    year = datetime.utcnow().year
    count = db.query(Complaint).count() + 1
    candidate = f"CMP-{year}-{count:04d}"

    # Verify uniqueness
    exists = db.query(Complaint).filter_by(complaint_id=candidate).first()
    if exists:
        suffix = uuid.uuid4().hex[:4].upper()
        candidate = f"CMP-{year}-{suffix}"
    return candidate


@router.post("/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)) -> Complaint:
    """Save a finalized complaint record to the database."""
    try:
        data = payload.model_dump(exclude_unset=True)

        complaint_id = data.get("complaint_id")
        if not complaint_id or not str(complaint_id).strip():
            complaint_id = _generate_complaint_id(db)
            data["complaint_id"] = complaint_id
        else:
            # Check if provided complaint_id already exists
            existing = db.query(Complaint).filter_by(complaint_id=complaint_id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Complaint with identifier '{complaint_id}' already exists."
                )

        new_complaint = Complaint(**data)
        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)
        return new_complaint

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to create complaint: %s", exc)
        raise HTTPException(status_code=500, detail=f"Database error while saving complaint: {str(exc)}")


@router.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)) -> List[Complaint]:
    """Retrieve all logged complaints ordered by creation date descending."""
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()


@router.get("/complaints/{id}", response_model=ComplaintResponse)
def get_complaint(id: str, db: Session = Depends(get_db)) -> Complaint:
    """Retrieve details of a single complaint by integer ID or complaint_id code."""
    complaint = None
    if id.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(id)).first()

    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.complaint_id == id).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with identifier '{id}' not found."
        )

    return complaint
