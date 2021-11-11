"""booking_deposit_id
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ee90200aa0db"
down_revision = "1ff543866ff9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("individual_booking", sa.Column("depositId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_individual_booking_depositId"), "individual_booking", ["depositId"], unique=False)
    op.create_foreign_key(None, "individual_booking", "deposit", ["depositId"], ["id"])


def downgrade():
    op.drop_column("individual_booking", "depositId")
