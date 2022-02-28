"""fix_nullable_fields_to_reflect_business_constraints
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "cc59756a1974"
down_revision = "ca95cbf376a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("offerVenue", postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    op.drop_column("collective_offer", "jsonData")
    op.alter_column(
        "collective_offer_template", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=False
    )
    op.alter_column("collective_stock", "numberOfTickets", existing_type=sa.INTEGER(), nullable=False)


def downgrade() -> None:
    op.alter_column("collective_stock", "numberOfTickets", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "collective_offer_template", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=True
    )
    op.add_column(
        "collective_offer",
        sa.Column("jsonData", postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    )
    op.drop_column("collective_offer", "offerVenue")
