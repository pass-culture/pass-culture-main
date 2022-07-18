"""add_column_to_tract_educational_institution_type
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "58102ed26597"
down_revision = "d06b794e8ced"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("educational_institution", sa.Column("institutionType", sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column("educational_institution", "institutionType")
