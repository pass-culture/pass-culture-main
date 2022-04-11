"""text_contact_phone_collective_offer
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bc19bb0b294f"
down_revision = "a02d2297669c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE collective_offer_template ALTER COLUMN "contactPhone" TYPE text;')
    op.execute('ALTER TABLE collective_offer ALTER COLUMN "contactPhone" TYPE text;')


def downgrade() -> None:
    op.execute('ALTER TABLE collective_offer ALTER COLUMN "contactPhone" TYPE VARCHAR(20);')
    op.execute('ALTER TABLE collective_offer_template ALTER COLUMN "contactPhone" TYPE VARCHAR(20);')
