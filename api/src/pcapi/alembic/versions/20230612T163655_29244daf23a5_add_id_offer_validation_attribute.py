"""
Add OfferValidationAttribute ID
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "29244daf23a5"
down_revision = "df422d433b32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE 'ID'")


def downgrade() -> None:
    # can't drop value of a type
    pass
