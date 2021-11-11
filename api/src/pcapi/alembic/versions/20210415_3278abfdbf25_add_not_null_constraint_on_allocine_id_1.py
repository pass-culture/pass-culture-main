"""add_not_null_constraint_on_allocine_id_1

Revision ID: 3278abfdbf25
Revises: ccf69bc028ef
Create Date: 2021-04-15 09:25:42.413449

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "3278abfdbf25"
down_revision = "ccf69bc028ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE allocine_venue_provider ADD CONSTRAINT internal_id_not_null_constraint CHECK ("internalId" IS NOT NULL) NOT VALID;
            ALTER TABLE allocine_pivot ADD CONSTRAINT internal_id_not_null_constraint CHECK ("internalId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("internal_id_not_null_constraint", table_name="allocine_venue_provider")
    op.drop_constraint("internal_id_not_null_constraint", table_name="allocine_pivot")
