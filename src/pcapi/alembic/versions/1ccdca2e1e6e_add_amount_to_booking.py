"""Add amount to booking

Revision ID: 1ccdca2e1e6e
Create Date: 2018-07-26 11:52:17.853134

"""
from alembic import op


# revision identifiers, used by Alembic.

revision = "1ccdca2e1e6e"
down_revision = "5f81d0abe040"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        'ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);'
        'UPDATE booking b SET amount=(SELECT o.price FROM offer o WHERE o.id=b."offerId");'
        'DELETE FROM booking WHERE "offerId" IS NULL;'
        'ALTER TABLE "booking" ALTER COLUMN "amount" SET NOT NULL;'
        'ALTER TABLE "booking" ALTER COLUMN "offerId" SET NOT NULL;'
    )


def downgrade():
    pass
