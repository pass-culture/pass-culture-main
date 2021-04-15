"""add_not_null_constraint_on_allocine_id_3

Revision ID: dd8b39c4beee
Revises: d8a4ae2a6a1c
Create Date: 2021-04-15 09:32:36.476606

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "dd8b39c4beee"
down_revision = "d8a4ae2a6a1c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("allocine_venue_provider", "internalId", nullable=False)
    op.alter_column("allocine_pivot", "internalId", nullable=False)


def downgrade() -> None:
    op.alter_column("allocine_venue_provider", "internalId", nullable=True)
    op.alter_column("allocine_pivot", "internalId", nullable=True)
