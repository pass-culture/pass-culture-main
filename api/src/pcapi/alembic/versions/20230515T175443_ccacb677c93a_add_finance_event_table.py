"""Add finance_event table"""

from alembic import op
import sqlalchemy as sa

import pcapi.utils


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ccacb677c93a"
down_revision = "4a9bc6a57da0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    import pcapi.core.finance.models as finance_models

    op.create_table(
        "finance_event",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("valueDate", sa.DateTime(), nullable=False),
        sa.Column("pricingOrderingDate", sa.DateTime(), nullable=True),
        sa.Column("status", pcapi.utils.db.MagicEnum(finance_models.FinanceEventStatus), nullable=False),
        sa.Column("motive", pcapi.utils.db.MagicEnum(finance_models.FinanceEventMotive), nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=True),
        sa.Column("collectiveBookingId", sa.BigInteger(), nullable=True),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("pricingPointId", sa.BigInteger(), nullable=True),
        sa.CheckConstraint('num_nonnulls("bookingId", "collectiveBookingId") = 1'),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_finance_event_bookingId"), "finance_event", ["bookingId"], unique=False)
    op.create_index(
        op.f("ix_finance_event_collectiveBookingId"), "finance_event", ["collectiveBookingId"], unique=False
    )
    op.create_index(op.f("ix_finance_event_pricingPointId"), "finance_event", ["pricingPointId"], unique=False)
    op.create_index(op.f("ix_finance_event_status"), "finance_event", ["status"], unique=False)
    op.create_index(op.f("ix_finance_event_venueId"), "finance_event", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_table("finance_event")
