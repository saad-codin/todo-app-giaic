"""Authentication routes."""

import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr

from db import get_session
from models import User, UserCreate, UserResponse
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    set_auth_cookie,
    clear_auth_cookie,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    """Sign up request body."""
    email: EmailStr
    password: str
    name: str | None = None


class SignInRequest(BaseModel):
    """Sign in request body."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Auth response body."""
    user: UserResponse


class SuccessResponse(BaseModel):
    """Success response body."""
    success: bool


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignUpRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    """Create a new user account."""
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": "Email already exists"},
        )

    # Validate password
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Password must be at least 8 characters",
                "details": {"field": "password", "constraint": "minLength"},
            },
        )

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        name=request.name,
        hashed_password=get_password_hash(request.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create token and set cookie
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    set_auth_cookie(response, access_token)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            createdAt=user.created_at.isoformat() + "Z",
        )
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SignInRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    """Authenticate user and return JWT."""
    user = session.exec(select(User).where(User.email == request.email)).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"},
        )

    # Create token and set cookie
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    set_auth_cookie(response, access_token)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            createdAt=user.created_at.isoformat() + "Z",
        )
    )


@router.post("/signout", response_model=SuccessResponse)
async def signout(response: Response):
    """Sign out current user."""
    clear_auth_cookie(response)
    return SuccessResponse(success=True)


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return AuthResponse(
        user=UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            createdAt=current_user.created_at.isoformat() + "Z",
        )
    )
