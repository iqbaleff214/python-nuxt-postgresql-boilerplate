"""Initial schema: users, tokens, notifications

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column(
            "role",
            sa.Enum("superadmin", "user", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "banned", name="userstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "is_email_verified",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("totp_secret", sa.Text, nullable=True),
        sa.Column(
            "is_2fa_enabled",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_status", "users", ["status"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])

    # ── tokens ────────────────────────────────────────────────────────────────
    op.create_table(
        "tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "refresh",
                "email_verify",
                "password_reset",
                "email_change",
                "delete_cancel",
                "mfa_challenge",
                "totp_recovery",
                "mfa_setup",
                name="tokentype",
            ),
            nullable=False,
        ),
        sa.Column("metadata", JSON, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_tokens_user_id_users",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_tokens_user_id", "tokens", ["user_id"])
    op.create_index("ix_tokens_token", "tokens", ["token"])
    op.create_index("ix_tokens_type", "tokens", ["type"])
    op.create_index("ix_tokens_expires_at", "tokens", ["expires_at"])

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_notifications_user_id_users",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_read_at", "notifications", ["read_at"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_notifications_created_at", "notifications")
    op.drop_index("ix_notifications_read_at", "notifications")
    op.drop_index("ix_notifications_user_id", "notifications")
    op.drop_table("notifications")
    op.drop_index("ix_tokens_expires_at", "tokens")
    op.drop_index("ix_tokens_type", "tokens")
    op.drop_index("ix_tokens_token", "tokens")
    op.drop_index("ix_tokens_user_id", "tokens")
    op.drop_table("tokens")
    op.drop_index("ix_users_deleted_at", "users")
    op.drop_index("ix_users_role", "users")
    op.drop_index("ix_users_status", "users")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS tokentype")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
