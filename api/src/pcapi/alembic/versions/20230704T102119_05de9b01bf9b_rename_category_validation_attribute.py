"""Rename OfferValidationAttribute Category to CategoryId
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "05de9b01bf9b"
down_revision = "3eb1ca346ea8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute RENAME VALUE 'CATEGORY' TO 'CATEGORY_ID'")


def downgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute RENAME VALUE 'CATEGORY_ID' TO 'CATEGORY'")
