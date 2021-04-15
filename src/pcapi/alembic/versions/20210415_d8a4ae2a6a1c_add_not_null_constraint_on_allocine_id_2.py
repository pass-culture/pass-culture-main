"""add_not_null_constraint_on_allocine_id_2

Revision ID: d8a4ae2a6a1c
Revises: 3278abfdbf25
Create Date: 2021-04-15 09:30:38.654251

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d8a4ae2a6a1c"
down_revision = "3278abfdbf25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE allocine_venue_provider VALIDATE CONSTRAINT internal_id_not_null_constraint;")
    op.execute("ALTER TABLE allocine_pivot VALIDATE CONSTRAINT internal_id_not_null_constraint;")


def downgrade() -> None:
    pass
