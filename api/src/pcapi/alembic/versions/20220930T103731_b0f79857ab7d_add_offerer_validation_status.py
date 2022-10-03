"""add_offerer_validation_status
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b0f79857ab7d"
down_revision = "246156d69d6f"
branch_labels = None
depends_on = None


ValidationStatus = sa.Enum("NEW", "PENDING", "VALIDATED", "REJECTED", name="validationstatus")


def upgrade() -> None:
    ValidationStatus.create(op.get_bind(), checkfirst=True)
    op.add_column("offerer", sa.Column("validationStatus", ValidationStatus, nullable=True))


def downgrade() -> None:
    op.drop_column("offerer", "validationStatus")
    ValidationStatus.drop(op.get_bind())
