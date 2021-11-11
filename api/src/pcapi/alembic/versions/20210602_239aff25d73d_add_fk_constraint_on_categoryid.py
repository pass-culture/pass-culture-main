"""add FK constraint on categoryId

Revision ID: 239aff25d73d
Revises: 0006642d26a1
Create Date: 2021-06-02 15:31:54.682545

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "239aff25d73d"
down_revision = "0006642d26a1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE offer ADD CONSTRAINT "offer_subcategoryId_fkey" FOREIGN KEY ("subcategoryId") REFERENCES "offer_subcategory" ("id") NOT VALID
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE offer DROP CONSTRAINT "offer_subcategoryId_fkey"
        """
    )
