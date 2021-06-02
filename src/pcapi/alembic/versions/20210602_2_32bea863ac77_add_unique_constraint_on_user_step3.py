"""Add unique constraint on user.idPieceNumber step 3

Revision ID: 32bea863ac77
Revises: 8bad2344ab11
Create Date: 2021-06-02 15:28:20.768526

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "32bea863ac77"
down_revision = "8bad2344ab11"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """ALTER TABLE "user" ADD CONSTRAINT "user_idPieceNumber_key" UNIQUE USING INDEX "user_idPieceNumber_key";"""
    )


def downgrade():
    op.execute("""ALTER TABLE "user" DROP CONSTRAINT "user_idPieceNumber_key";""")
