"""create_educational_institution_table

Revision ID: d49958abc723
Revises: 76d2efd6ad7e
Create Date: 2021-06-25 15:45:15.238772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d49958abc723"
down_revision = "76d2efd6ad7e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "educational_institution",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("institutionId", sa.String(30), nullable=False, unique=True, index=True),
    )


def downgrade():
    op.drop_table("educational_institution")
