"""Add user.idPieceNumber column varchar step 1

Revision ID: eb1fe3e8a43f
Revises: 5bca073597c4
Create Date: 2021-05-28 16:30:57.890929

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "eb1fe3e8a43f"
down_revision = "5bca073597c4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""ALTER TABLE "user" ADD COLUMN "idPieceNumber" VARCHAR;""")


def downgrade():
    op.drop_column("user", "idPieceNumber")
