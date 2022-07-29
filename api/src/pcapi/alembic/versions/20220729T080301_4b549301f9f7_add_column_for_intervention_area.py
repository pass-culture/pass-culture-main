"""add_column_for_intervention_area
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4b549301f9f7"
down_revision = "aed2f6174add"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer",
        sa.Column("interventionArea", postgresql.ARRAY(sa.Text()), server_default="{}", nullable=False),
    )
    op.add_column(
        "collective_offer_template",
        sa.Column("interventionArea", postgresql.ARRAY(sa.Text()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("collective_offer_template", "interventionArea")
    op.drop_column("collective_offer", "interventionArea")
