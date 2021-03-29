"""add_internal_id_to_allocine_venue_provider

Revision ID: 202ae94f2c8f
Revises: 5a767131f3ec
Create Date: 2021-03-29 09:27:06.343973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202ae94f2c8f"
down_revision = "5a767131f3ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("allocine_venue_provider", sa.Column("internalId", sa.Text, nullable=True))
    op.create_unique_constraint(None, "allocine_venue_provider", ["internalId"])


def downgrade() -> None:
    op.drop_constraint(None, "allocine_venue_provider", type_="unique")
    op.drop_column("allocine_venue_provider", "internalId")
