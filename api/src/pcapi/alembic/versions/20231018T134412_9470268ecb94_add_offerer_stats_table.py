"""
add offerer_stats table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9470268ecb94"
down_revision = "d12371e730c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offerer_stats",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("syncDate", sa.DateTime(), nullable=False),
        sa.Column("table", sa.String(length=120), nullable=False),
        sa.Column("jsonData", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("offererId", "table", name="offerer_stats_unique"),
    )
    op.create_index("ix_offerer_stats_offererId", "offerer_stats", ["offererId"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_offerer_stats_offererId", table_name="offerer_stats")
    op.drop_table("offerer_stats")
