"""educational_institution_add_adageId_field

Revision ID: 3c46248f7143
Revises: d8b409a3cf0c
Create Date: 2021-06-29 15:38:50.855795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c46248f7143"
down_revision = "d8b409a3cf0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("educational_year", sa.Column("adageId", sa.String(length=30), nullable=False))
    op.create_unique_constraint(None, "educational_year", ["adageId"])


def downgrade() -> None:
    op.drop_column("educational_year", "adageId")
