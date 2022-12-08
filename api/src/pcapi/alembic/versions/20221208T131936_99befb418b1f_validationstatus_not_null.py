"""validationStatus_not_null
"""
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "99befb418b1f"
down_revision = "47bf17f0d7e9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "offerer",
        "validationStatus",
        existing_type=postgresql.ENUM("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus"),
        nullable=False,
    )
    op.alter_column(
        "user_offerer",
        "validationStatus",
        existing_type=postgresql.ENUM("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus"),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "user_offerer",
        "validationStatus",
        existing_type=postgresql.ENUM("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus"),
        nullable=True,
    )
    op.alter_column(
        "offerer",
        "validationStatus",
        existing_type=postgresql.ENUM("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus"),
        nullable=True,
    )
