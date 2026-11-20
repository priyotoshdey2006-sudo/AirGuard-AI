"""Authentication and user profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserProfile
from app.schemas.user import (
    Token,
    UserLogin,
    UserProfileResponse,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Register new citizen account and initialize health sensitivity profile."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    new_user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(new_user)
    db.flush()

    new_profile = UserProfile(
        user_id=new_user.id,
        sensitivity_level=payload.sensitivity_level.upper(),
    )
    db.add(new_profile)
    db.commit()

    token = create_access_token(
        subject=new_user.id,
        extra_claims={"email": new_user.email, "role": new_user.role},
    )
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate citizen credentials and issue Bearer JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(
        subject=user.id,
        extra_claims={"email": user.email, "role": user.role},
    )
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve authenticated user data and health preferences."""
    user = db.query(User).filter(User.id == current_user.id).first()

    profile_resp = None
    if user.profile:
        profile_resp = UserProfileResponse(
            id=user.profile.id,
            sensitivity_level=user.profile.sensitivity_level,
            home_lat=user.profile.home_lat,
            home_lon=user.profile.home_lon,
            work_lat=user.profile.work_lat,
            work_lon=user.profile.work_lon,
            notify_on_poor_aqi=user.profile.notify_on_poor_aqi,
            alert_threshold_aqi=user.profile.alert_threshold_aqi,
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        profile=profile_resp,
    )


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update respiratory sensitivity, coordinate anchors, and alert thresholds."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if payload.sensitivity_level:
        profile.sensitivity_level = payload.sensitivity_level.upper()
    if payload.home_lat is not None:
        profile.home_lat = payload.home_lat
    if payload.home_lon is not None:
        profile.home_lon = payload.home_lon
    if payload.work_lat is not None:
        profile.work_lat = payload.work_lat
    if payload.work_lon is not None:
        profile.work_lon = payload.work_lon
    if payload.notify_on_poor_aqi is not None:
        profile.notify_on_poor_aqi = payload.notify_on_poor_aqi
    if payload.alert_threshold_aqi is not None:
        profile.alert_threshold_aqi = payload.alert_threshold_aqi

    db.commit()
    db.refresh(profile)

    return UserProfileResponse(
        id=profile.id,
        sensitivity_level=profile.sensitivity_level,
        home_lat=profile.home_lat,
        home_lon=profile.home_lon,
        work_lat=profile.work_lat,
        work_lon=profile.work_lon,
        notify_on_poor_aqi=profile.notify_on_poor_aqi,
        alert_threshold_aqi=profile.alert_threshold_aqi,
    )
