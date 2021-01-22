"""Drop the mediation without offer (Step 0/4)

Revision ID: 06a7f387d996
Revises: bce80c4f574f
Create Date: 2021-01-22 10:07:29.071338

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "06a7f387d996"
down_revision = "bce80c4f574f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""DELETE FROM "mediation" WHERE "offerId" IS NULL;""")


def downgrade() -> None:
    pass
