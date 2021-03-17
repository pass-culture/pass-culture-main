"""add_not_null_venue_creation_date_step_2

Revision ID: 48125f3899cb
Revises: 3d149d0afa76
Create Date: 2021-03-17 17:27:53.908367

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "48125f3899cb"
down_revision = "3d149d0afa76"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE venue VALIDATE CONSTRAINT date_created_not_null_constraint;")


def downgrade() -> None:
    pass
