"""add_internal_id_to_allocine_pivot

Revision ID: 5a767131f3ec
Revises: 0f9f0a4ae98d
Create Date: 2021-03-29 09:10:45.541428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5a767131f3ec"
down_revision = "0f9f0a4ae98d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("allocine_pivot", sa.Column("internalId", sa.Text, nullable=True))
    op.create_unique_constraint(None, "allocine_pivot", ["internalId"])


def downgrade() -> None:
    op.drop_constraint(None, "allocine_pivot", type_="unique")
    op.drop_column("allocine_pivot", "internalId")
