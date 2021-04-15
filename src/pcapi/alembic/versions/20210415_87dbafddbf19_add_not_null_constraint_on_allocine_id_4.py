"""add_not_null_constraint_on_allocine_id_4

Revision ID: 87dbafddbf19
Revises: dd8b39c4beee
Create Date: 2021-04-15 09:42:53.806582

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "87dbafddbf19"
down_revision = "dd8b39c4beee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("internal_id_not_null_constraint", table_name="allocine_venue_provider")
    op.drop_constraint("internal_id_not_null_constraint", table_name="allocine_pivot")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE allocine_venue_provider ADD CONSTRAINT internal_id_not_null_constraint CHECK ("internalId" IS NOT NULL) NOT VALID;
            ALTER TABLE allocine_pivot ADD CONSTRAINT internal_id_not_null_constraint CHECK ("internalId" IS NOT NULL) NOT VALID;
        """
    )
