from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from src.auth.service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.database.connection import get_db
from src.database.models import (
    Achievement,
    ChallengeProgress,
    Cycle,
    DailyTask,
    MicroSprint,
    PendingTaskEffect,
    Plan,
    Progress,
    QuizAnswer,
    SeasonEvent,
    TaskLibrarySelection,
    User,
    WeeklyReport,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Create a new user account and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    await db.flush()

    progress = Progress(user_id=user.id)
    db.add(progress)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate with email and password, return JWT tokens."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Exchange a valid refresh token for a new access token pair."""
    try:
        user_id = decode_token(body.refresh_token, expected_type="refresh")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    """Return the current authenticated user's profile."""
    return user


@router.post("/complete-onboarding", response_model=UserResponse)
async def complete_onboarding(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Mark the user as onboarded and set plan_start_date to today."""
    if user.onboarded:
        return user

    user.onboarded = True
    user.plan_start_date = date.today()
    user.program_day = 1
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete the user and all associated data."""
    uid = user.id

    # Cascade-delete from child tables in dependency order
    cascade_tables = [
        PendingTaskEffect,
        SeasonEvent,
        WeeklyReport,
        MicroSprint,
        Achievement,
        ChallengeProgress,
        Cycle,
        TaskLibrarySelection,
        DailyTask,
        Plan,
        Progress,
        QuizAnswer,
    ]
    for model in cascade_tables:
        await db.execute(delete(model).where(model.user_id == uid))

    await db.execute(delete(User).where(User.id == uid))
