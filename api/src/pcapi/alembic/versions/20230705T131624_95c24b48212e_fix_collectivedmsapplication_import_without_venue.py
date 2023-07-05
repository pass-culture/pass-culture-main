"""Rework table collective_dms_application to handle dms application with unknown siret
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "95c24b48212e"
down_revision = "4a8eec2f9eff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_collective_dms_application_venueId", table_name="collective_dms_application")
    op.drop_constraint("collective_dms_application_venueId_fkey", "collective_dms_application", type_="foreignkey")
    op.drop_column("collective_dms_application", "venueId")


def downgrade() -> None:
    op.add_column("collective_dms_application", sa.Column("venueId", sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_foreign_key(
        "collective_dms_application_venueId_fkey", "collective_dms_application", "venue", ["venueId"], ["id"]
    )
    op.create_index("ix_collective_dms_application_venueId", "collective_dms_application", ["venueId"], unique=False)
