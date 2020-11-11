"""delete_duplicate_favorites_and_add_unicity_constraint

Revision ID: 621aad6436f9
Revises: a762ac64ec33
Create Date: 2019-09-27 13:58:45.645802

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "621aad6436f9"
down_revision = "a762ac64ec33"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DELETE FROM favorite f1
        USING favorite f2
        WHERE f1.id < f2.id
            AND f1."offerId" = f2."offerId"
            AND f1."userId"  = f2."userId"
    """
    )
    op.create_unique_constraint("unique_favorite", "favorite", ["userId", "offerId"])


def downgrade():
    op.drop_constraint("unique_favorite", "favorite")
