"""add_validation_to_offer

Revision ID: 6cc6a0de4be6
Revises: 9531102bcb21
Create Date: 2021-03-04 13:06:42.534309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6cc6a0de4be6"
down_revision = "9531102bcb21"
branch_labels = None
depends_on = None


ValidationStatus = sa.Enum("APPROVED", "AWAITING", "REJECTED", name="validation_status")


def upgrade():
    ValidationStatus.create(op.get_bind(), checkfirst=True)
    op.add_column("offer", sa.Column("validation", ValidationStatus, nullable=False, server_default="APPROVED"))


def downgrade():
    op.drop_column("offer", "validation")
    ValidationStatus.drop(op.get_bind())
