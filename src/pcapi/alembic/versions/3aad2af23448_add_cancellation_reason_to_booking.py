"""add_cancellation_reason_to_booking

Revision ID: 3aad2af23448
Revises: 8c366d4230c7
Create Date: 2020-11-25 09:11:22.869206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3aad2af23448"
down_revision = "8c366d4230c7"
branch_labels = None
depends_on = None


CancellationReasons = sa.Enum("OFFERER", "BENEFICIARY", "EXPIRED", name="cancellation_reason")


def upgrade():
    CancellationReasons.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "booking",
        sa.Column(
            "cancellationReason",
            CancellationReasons,
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("booking", "cancellationReason")
    CancellationReasons.drop(op.get_bind())
