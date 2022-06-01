"""add_educational_redactor_on_collective_booking_model
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "75adc304cc89"
down_revision = "ab181e95a4c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_booking", sa.Column("educationalRedactorId", sa.BigInteger(), nullable=False))
    op.create_index(
        op.f("ix_collective_booking_educationalRedactorId"),
        "collective_booking",
        ["educationalRedactorId"],
        unique=False,
    )
    op.create_foreign_key(None, "collective_booking", "educational_redactor", ["educationalRedactorId"], ["id"])


def downgrade() -> None:
    op.drop_column("collective_booking", "educationalRedactorId")
