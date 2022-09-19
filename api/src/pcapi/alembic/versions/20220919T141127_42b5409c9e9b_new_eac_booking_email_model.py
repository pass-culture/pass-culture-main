"""new_eac_booking_email_model
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "42b5409c9e9b"
down_revision = "53b7d749990e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer",
        sa.Column("bookingEmails", postgresql.ARRAY(sa.String()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("collective_offer", "bookingEmails")
