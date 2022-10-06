"""add_validation_status_to_user_offerer
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1f1858336c2"
down_revision = "ac10b3d69c25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_offerer",
        sa.Column(
            "validationStatus",
            sa.Enum("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_offerer", "validationStatus")
