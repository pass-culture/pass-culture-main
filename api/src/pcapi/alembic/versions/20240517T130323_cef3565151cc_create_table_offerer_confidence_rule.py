"""Create table: offerer_confidence_rule
"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.offerers.models import OffererConfidenceLevel
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cef3565151cc"
down_revision = "048bdcee32e9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offerer_confidence_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=True),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("confidenceLevel", MagicEnum(OffererConfidenceLevel), nullable=False),
        sa.CheckConstraint('num_nonnulls("offererId", "venueId") = 1'),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_offerer_confidence_rule_offererId"), "offerer_confidence_rule", ["offererId"], unique=True)
    op.create_index(op.f("ix_offerer_confidence_rule_venueId"), "offerer_confidence_rule", ["venueId"], unique=True)


def downgrade() -> None:
    op.drop_table("offerer_confidence_rule")
