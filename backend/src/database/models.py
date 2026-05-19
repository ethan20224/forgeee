import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Group 1 — Users & Auth
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Program state
    program_day: Mapped[int] = mapped_column(Integer, default=1)
    season: Mapped[int] = mapped_column(Integer, default=1)
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    plan_start_date: Mapped[date | None] = mapped_column(Date)
    timezone: Mapped[str] = mapped_column(Text, default="UTC")
    last_active_date: Mapped[date | None] = mapped_column(Date)

    # Photo & face
    baseline_photo_url: Mapped[str | None] = mapped_column(Text)
    baseline_photo_path: Mapped[str | None] = mapped_column(Text)
    face_shape: Mapped[str | None] = mapped_column(Text)

    # Referrals
    referral_code: Mapped[str | None] = mapped_column(Text, unique=True)
    referred_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )

    # Gamification
    first_strike_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(Text, nullable=False, default="none")
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    subscription_provider: Mapped[str] = mapped_column(Text, nullable=False, default="revenuecat")

    # AI
    initial_compliment: Mapped[str | None] = mapped_column(Text)

    # Relationships
    quiz_answers: Mapped[list["QuizAnswer"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    progress: Mapped["Progress | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    cycles: Mapped[list["Cycle"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("season >= 1 AND season <= 99", name="ck_users_season_range"),
        CheckConstraint(
            "name IS NULL OR LENGTH(name) BETWEEN 1 AND 100",
            name="ck_users_name_length",
        ),
    )


# ---------------------------------------------------------------------------
# Group 2 — Programs & Tasks
# ---------------------------------------------------------------------------


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    goals: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    routine_level: Mapped[str | None] = mapped_column(Text)
    daily_time: Mapped[str | None] = mapped_column(Text)
    timeline: Mapped[str | None] = mapped_column(Text)
    main_concern: Mapped[str | None] = mapped_column(Text)
    age_range: Mapped[str | None] = mapped_column(Text)
    has_photo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="quiz_answers")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    season: Mapped[int] = mapped_column(Integer, default=1)
    program_name: Mapped[str | None] = mapped_column(Text)
    focus_summary: Mapped[str | None] = mapped_column(Text)
    honest_expectation: Mapped[str | None] = mapped_column(Text)
    raw_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="plans")
    daily_tasks: Mapped[list["DailyTask"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )
    task_library_selections: Mapped[list["TaskLibrarySelection"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_works: Mapped[str | None] = mapped_column(Text)
    duration_mins: Mapped[int | None] = mapped_column(Integer)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_value: Mapped[int] = mapped_column(Integer, default=10)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    library_task_id: Mapped[str | None] = mapped_column(Text)
    pillar: Mapped[str] = mapped_column(Text, nullable=False, default="skin")
    tier: Mapped[str] = mapped_column(Text, nullable=False, default="beginner")
    week_number: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    plan: Mapped["Plan"] = relationship(back_populates="daily_tasks")

    __table_args__ = (
        Index("idx_daily_tasks_user_day", "user_id", "day_number"),
        Index("idx_daily_tasks_week_pillar", "user_id", "week_number", "pillar"),
        CheckConstraint("xp_value >= 0", name="ck_daily_tasks_xp_positive"),
        CheckConstraint("day_number >= 1", name="ck_daily_tasks_day_positive"),
    )


class TaskLibrarySelection(Base):
    __tablename__ = "task_library_selections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False
    )
    library_task_id: Mapped[str] = mapped_column(Text, nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=1)
    season: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    plan: Mapped["Plan"] = relationship(back_populates="task_library_selections")


# ---------------------------------------------------------------------------
# Group 3 — Progress & Scoring
# ---------------------------------------------------------------------------


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)

    # 9-pillar scores (all default 50)
    facial_composition_score: Mapped[int] = mapped_column(Integer, default=50)
    skin_score: Mapped[int] = mapped_column(Integer, default=50)
    grooming_score: Mapped[int] = mapped_column(Integer, default=50)
    hair_score: Mapped[int] = mapped_column(Integer, default=50)
    posture_score: Mapped[int] = mapped_column(Integer, default=50)
    style_score: Mapped[int] = mapped_column(Integer, default=50)
    sleep_score: Mapped[int] = mapped_column(Integer, default=50)
    nutrition_score: Mapped[int] = mapped_column(Integer, default=50)
    voice_score: Mapped[int] = mapped_column(Integer, default=50)

    optimisation_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("50.00"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(back_populates="progress")

    __table_args__ = (
        CheckConstraint("facial_composition_score BETWEEN 0 AND 100", name="ck_progress_facial"),
        CheckConstraint("skin_score BETWEEN 0 AND 100", name="ck_progress_skin"),
        CheckConstraint("grooming_score BETWEEN 0 AND 100", name="ck_progress_grooming"),
        CheckConstraint("hair_score BETWEEN 0 AND 100", name="ck_progress_hair"),
        CheckConstraint("posture_score BETWEEN 0 AND 100", name="ck_progress_posture"),
        CheckConstraint("style_score BETWEEN 0 AND 100", name="ck_progress_style"),
        CheckConstraint("sleep_score BETWEEN 0 AND 100", name="ck_progress_sleep"),
        CheckConstraint("nutrition_score BETWEEN 0 AND 100", name="ck_progress_nutrition"),
        CheckConstraint("voice_score BETWEEN 0 AND 100", name="ck_progress_voice"),
        CheckConstraint("optimisation_score BETWEEN 0 AND 100", name="ck_progress_optimisation"),
        CheckConstraint("current_streak >= 0", name="ck_progress_streak_positive"),
        CheckConstraint("longest_streak >= 0", name="ck_progress_longest_positive"),
        CheckConstraint("total_xp >= 0", name="ck_progress_xp_positive"),
    )


# ---------------------------------------------------------------------------
# Group 4 — Cycles
# ---------------------------------------------------------------------------


class Cycle(Base):
    __tablename__ = "cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(Text)
    photo_path: Mapped[str | None] = mapped_column(Text)
    cycle_type: Mapped[str] = mapped_column(Text, default="regular")
    face_shape: Mapped[str | None] = mapped_column(Text)

    # 9-pillar scores (nullable — not all assessed per cycle)
    facial_composition_score: Mapped[int | None] = mapped_column(Integer)
    skin_score: Mapped[int | None] = mapped_column(Integer)
    grooming_score: Mapped[int | None] = mapped_column(Integer)
    hair_score: Mapped[int | None] = mapped_column(Integer)
    posture_score: Mapped[int | None] = mapped_column(Integer)
    style_score: Mapped[int | None] = mapped_column(Integer)
    sleep_score: Mapped[int | None] = mapped_column(Integer)
    nutrition_score: Mapped[int | None] = mapped_column(Integer)
    voice_score: Mapped[int | None] = mapped_column(Integer)

    ai_insight: Mapped[str | None] = mapped_column(Text)
    next_focus: Mapped[str | None] = mapped_column(Text)
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(back_populates="cycles")

    __table_args__ = (
        UniqueConstraint("user_id", "cycle_number", name="uq_cycles_user_number"),
        Index("idx_cycles_user_type", "user_id", "cycle_type"),
        CheckConstraint(
            "facial_composition_score IS NULL OR facial_composition_score BETWEEN 0 AND 100",
            name="ck_cycles_facial",
        ),
        CheckConstraint(
            "skin_score IS NULL OR skin_score BETWEEN 0 AND 100",
            name="ck_cycles_skin",
        ),
        CheckConstraint(
            "grooming_score IS NULL OR grooming_score BETWEEN 0 AND 100",
            name="ck_cycles_grooming",
        ),
        CheckConstraint(
            "hair_score IS NULL OR hair_score BETWEEN 0 AND 100",
            name="ck_cycles_hair",
        ),
        CheckConstraint(
            "posture_score IS NULL OR posture_score BETWEEN 0 AND 100",
            name="ck_cycles_posture",
        ),
        CheckConstraint(
            "style_score IS NULL OR style_score BETWEEN 0 AND 100",
            name="ck_cycles_style",
        ),
        CheckConstraint(
            "sleep_score IS NULL OR sleep_score BETWEEN 0 AND 100",
            name="ck_cycles_sleep",
        ),
        CheckConstraint(
            "nutrition_score IS NULL OR nutrition_score BETWEEN 0 AND 100",
            name="ck_cycles_nutrition",
        ),
        CheckConstraint(
            "voice_score IS NULL OR voice_score BETWEEN 0 AND 100",
            name="ck_cycles_voice",
        ),
    )


# ---------------------------------------------------------------------------
# Group 5 — Gamification
# ---------------------------------------------------------------------------


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    badge_id: Mapped[str] = mapped_column(Text, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="achievements")

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_achievements_user_badge"),)


class ChallengeProgress(Base):
    __tablename__ = "challenge_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="active")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    target: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("target > 0", name="ck_challenge_target_positive"),
        CheckConstraint("progress >= 0", name="ck_challenge_progress_positive"),
    )


# ---------------------------------------------------------------------------
# Group 6 — Coaching
# ---------------------------------------------------------------------------


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    season: Mapped[int] = mapped_column(Integer, default=1)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)


class MicroSprint(Base):
    __tablename__ = "micro_sprints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sprint_type: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tasks: Mapped[dict] = mapped_column(JSONB, nullable=False)


# ---------------------------------------------------------------------------
# Group 7 — System
# ---------------------------------------------------------------------------


class SeasonEvent(Base):
    __tablename__ = "season_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    from_season: Mapped[int] = mapped_column(Integer, nullable=False)
    to_season: Mapped[int | None] = mapped_column(Integer)
    event_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    __table_args__ = (Index("idx_season_events_user_created", "user_id", "created_at"),)


class PendingTaskEffect(Base):
    __tablename__ = "pending_task_effects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    pillar: Mapped[str] = mapped_column(Text, nullable=False)
    drift: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.5"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ---------------------------------------------------------------------------
# NEW — Plan Cache (quiz-answer hash → cached plan)
# ---------------------------------------------------------------------------


class PlanCache(Base):
    __tablename__ = "plan_cache"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    plan_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    hit_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (Index("idx_plan_cache_hash", "quiz_hash"),)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: SQLAlchemy ORM models for all 14 FORGE database tables.

Flow:
1. Base declarative class shared by all models
2. Models map 1:1 to PostgreSQL tables with constraints and indexes
3. Relationships defined for FK traversal (user → plans, plan → tasks, etc.)
4. Alembic uses these models to auto-generate migrations

Main Entry Point: Base (imported by Alembic env.py to discover all models)

Dependencies:
- sqlalchemy: ORM definitions
"""
