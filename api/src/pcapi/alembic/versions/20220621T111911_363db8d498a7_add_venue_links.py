"""Add venue_pricing_point_link, venue_reimbursement_point_link and new columns in pricing, cashflow and invoice."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "363db8d498a7"
down_revision = "cb1d904c149d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "venue_pricing_point_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("pricingPointId", sa.BigInteger(), nullable=False),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=False),
        postgresql.ExcludeConstraint((sa.column("venueId"), "="), (sa.column("timespan"), "&&"), using="gist"),
        sa.ForeignKeyConstraint(
            ["pricingPointId"],
            ["venue.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_venue_pricing_point_link_pricingPointId"), "venue_pricing_point_link", ["pricingPointId"], unique=False
    )
    op.create_index(op.f("ix_venue_pricing_point_link_venueId"), "venue_pricing_point_link", ["venueId"], unique=False)

    op.create_table(
        "venue_reimbursement_point_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("reimbursementPointId", sa.BigInteger(), nullable=False),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=False),
        postgresql.ExcludeConstraint((sa.column("venueId"), "="), (sa.column("timespan"), "&&"), using="gist"),
        sa.ForeignKeyConstraint(
            ["reimbursementPointId"],
            ["venue.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_venue_reimbursement_point_link_reimbursementPointId"),
        "venue_reimbursement_point_link",
        ["reimbursementPointId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_venue_reimbursement_point_link_venueId"), "venue_reimbursement_point_link", ["venueId"], unique=False
    )

    op.add_column("pricing", sa.Column("pricingPointId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_pricing_pricingPointId"), "pricing", ["pricingPointId"], unique=False)
    op.create_foreign_key(None, "pricing", "venue", ["pricingPointId"], ["id"])

    op.add_column("cashflow", sa.Column("reimbursementPointId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_cashflow_reimbursementPointId"), "cashflow", ["reimbursementPointId"], unique=False)
    op.create_foreign_key(None, "cashflow", "venue", ["reimbursementPointId"], ["id"])

    op.add_column("invoice", sa.Column("reimbursementPointId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_invoice_reimbursementPointId"), "invoice", ["reimbursementPointId"], unique=False)
    op.create_foreign_key(None, "invoice", "venue", ["reimbursementPointId"], ["id"])


def downgrade():
    op.drop_column("pricing", "pricingPointId")
    op.drop_column("invoice", "reimbursementPointId")
    op.drop_column("cashflow", "reimbursementPointId")
    op.drop_table("venue_reimbursement_point_link")
    op.drop_table("venue_pricing_point_link")
