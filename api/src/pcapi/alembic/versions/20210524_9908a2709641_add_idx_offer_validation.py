"""add_idx_offer_validation

Revision ID: 9908a2709641
Revises: 8bdc4df58856
Create Date: 2021-05-24 10:12:35.543128

"""
from alembic import op


revision = "9908a2709641"
down_revision = "8bdc4df58856"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_validation" ON offer ("validation")
        """
    )


def downgrade():
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_validation"
        """
    )
