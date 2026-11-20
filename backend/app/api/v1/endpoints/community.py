"""Community crowdsourced pollution hazard reporting endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user_optional, get_db
from app.models.community_report import CommunityReport
from app.models.user import User
from app.schemas.community import (
    CommunityReportCreate,
    CommunityReportList,
    CommunityReportResponse,
)
from app.services.geo_service import haversine_distance_km

router = APIRouter()


@router.get("/reports", response_model=CommunityReportList, tags=["Community Reports"])
def list_community_reports(
    lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    lon: Optional[float] = Query(None, ge=-180.0, le=180.0),
    radius_km: Optional[float] = Query(50.0, ge=1.0, le=500.0),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieve community-reported environmental hazards with optional spatial radius filter."""
    query = db.query(CommunityReport).order_by(CommunityReport.created_at.desc())
    if category and category.upper() != "ALL":
        query = query.filter(CommunityReport.category == category.upper())

    raw_reports = query.all()

    formatted_reports: List[CommunityReportResponse] = []
    for r in raw_reports:
        dist = None
        if lat is not None and lon is not None:
            dist = haversine_distance_km(lat, lon, r.latitude, r.longitude)
            if dist > radius_km:
                continue

        formatted_reports.append(
            CommunityReportResponse(
                id=r.id,
                title=r.title,
                description=r.description,
                category=r.category,
                severity=r.severity,
                latitude=r.latitude,
                longitude=r.longitude,
                image_url=r.image_url,
                status=r.status,
                upvotes_count=r.upvotes_count,
                reporter_name=r.reporter_name,
                created_at=r.created_at,
                distance_km=dist,
            )
        )

    return CommunityReportList(total=len(formatted_reports), reports=formatted_reports)


@router.post("/reports", response_model=CommunityReportResponse, status_code=status.HTTP_201_CREATED, tags=["Community Reports"])
def submit_community_report(
    payload: CommunityReportCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Submit a geo-tagged pollution report (stubble burning, industrial smoke, road dust)."""
    # Privacy protection: Round latitude and longitude to 3 decimals (~110m)
    rounded_lat = round(payload.latitude, 3)
    rounded_lon = round(payload.longitude, 3)

    reporter_name = payload.reporter_name
    if current_user and current_user.full_name:
        reporter_name = current_user.full_name

    new_report = CommunityReport(
        user_id=current_user.id if current_user else None,
        reporter_name=reporter_name,
        title=payload.title,
        description=payload.description,
        category=payload.category.upper(),
        severity=payload.severity,
        latitude=rounded_lat,
        longitude=rounded_lon,
        image_url=payload.image_url,
        status="PENDING",
        upvotes_count=1,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return CommunityReportResponse(
        id=new_report.id,
        title=new_report.title,
        description=new_report.description,
        category=new_report.category,
        severity=new_report.severity,
        latitude=new_report.latitude,
        longitude=new_report.longitude,
        image_url=new_report.image_url,
        status=new_report.status,
        upvotes_count=new_report.upvotes_count,
        reporter_name=new_report.reporter_name,
        created_at=new_report.created_at,
        distance_km=0.0,
    )


@router.post("/reports/{report_id}/upvote", tags=["Community Reports"])
def upvote_community_report(
    report_id: str,
    db: Session = Depends(get_db),
):
    """Upvote a hazard report to confirm its verification status."""
    report = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    report.upvotes_count += 1
    if report.upvotes_count >= 5 and report.status == "PENDING":
        report.status = "VERIFIED"

    db.commit()
    return {"id": report.id, "upvotes_count": report.upvotes_count, "status": report.status}
