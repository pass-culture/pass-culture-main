"""new_eac_booking_email_offer_template
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d19b9f8cf4d0"
down_revision = "42b5409c9e9b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer_template",
        sa.Column("bookingEmails", postgresql.ARRAY(sa.String()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("collective_offer_template", "bookingEmails")
