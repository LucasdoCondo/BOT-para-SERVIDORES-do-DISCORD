"""add ai_cache"""
from alembic import op
import sqlalchemy as sa

revision = "0002_ai_cache"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_cache",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("prompt", sa.String(), default=""),
        sa.Column("answer", sa.String(), default=""),
        sa.Column("hits", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_cache")
