"""Add index on user.idPieceNumber step 2

Revision ID: 8bad2344ab11
Revises: eb1fe3e8a43f
Create Date: 2021-06-02 15:27:04.898790

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8bad2344ab11"
down_revision = "eb1fe3e8a43f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""COMMIT;""")
    op.execute("""CREATE UNIQUE INDEX CONCURRENTLY "user_idPieceNumber_key" ON "user"("idPieceNumber");""")


def downgrade():
    op.execute("""DROP INDEX IF EXISTS "user_idPieceNumber_key";""")
