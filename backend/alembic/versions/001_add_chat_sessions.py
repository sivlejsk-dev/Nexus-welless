"""Add chat_sessions and chat_turns tables for persistent conversation sessions.

Revision ID: 001_add_chat_sessions
Revises:
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa

revision = "001_add_chat_sessions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("user_id", sa.CHAR(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("primary_domain", sa.String(64), nullable=False, server_default="general"),
        sa.Column("total_turns", sa.Integer, nullable=False, server_default="0"),
        sa.Column("active_turns", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "chat_turns",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("session_id", sa.CHAR(36), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("turn_index", sa.Integer, nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("domain", sa.String(64), nullable=False, server_default="general"),
        sa.Column("intent", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("chat_turns")
    op.drop_table("chat_sessions")
