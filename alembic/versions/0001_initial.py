"""initial: user_levels, warns, tickets, reminders, guild_configs"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_levels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guild_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("xp", sa.Integer(), default=0),
        sa.Column("level", sa.Integer(), default=1),
        sa.Column("message_count", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "warns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guild_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("mod_id", sa.BigInteger(), default=0),
        sa.Column("reason", sa.String(), default="Sem motivo"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guild_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("channel_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("status", sa.String(), index=True, default="open"),
        sa.Column("subject", sa.String(), default="Suporte"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("guild_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("channel_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), index=True, nullable=False),
        sa.Column("text", sa.String(), default=""),
        sa.Column("remind_at", sa.DateTime(), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "guild_configs",
        sa.Column("guild_id", sa.BigInteger(), primary_key=True),
        sa.Column("persona", sa.String(), default=""),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for t in ["guild_configs", "reminders", "tickets", "warns", "user_levels"]:
        op.drop_table(t)
