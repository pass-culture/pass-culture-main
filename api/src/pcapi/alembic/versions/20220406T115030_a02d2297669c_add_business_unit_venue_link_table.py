"""Add business_unit_venue_link table."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "a02d2297669c"
down_revision = "d6d472d2dfad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_unit_venue_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("businessUnitId", sa.BigInteger(), nullable=False),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=False),
        postgresql.ExcludeConstraint((sa.column("venueId"), "="), (sa.column("timespan"), "&&"), using="gist"),
        sa.ForeignKeyConstraint(
            ["businessUnitId"],
            ["business_unit.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_business_unit_venue_link_businessUnitId"), "business_unit_venue_link", ["businessUnitId"], unique=False
    )
    op.create_index(op.f("ix_business_unit_venue_link_venueId"), "business_unit_venue_link", ["venueId"], unique=False)


def downgrade():
    op.drop_table("business_unit_venue_link")
