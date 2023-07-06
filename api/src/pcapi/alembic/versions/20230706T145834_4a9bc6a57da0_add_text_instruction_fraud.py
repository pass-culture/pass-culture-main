""" Add TEXT item to the enumeration of fraud check
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4a9bc6a57da0"
down_revision = "aa58aa5cb418"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE 'TEXT'")


def downgrade() -> None:
    pass
