"""remove_booking_email_column_from_collective_offer_and_collective_offer_template_tables
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "705410a724b3"
down_revision = "4e55db3dc9c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("collective_offer", "bookingEmail")
    op.drop_column("collective_offer_template", "bookingEmail")


def downgrade() -> None:
    op.add_column(
        "collective_offer_template",
        sa.Column("bookingEmail", sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    )
    op.add_column(
        "collective_offer", sa.Column("bookingEmail", sa.VARCHAR(length=120), autoincrement=False, nullable=True)
    )
