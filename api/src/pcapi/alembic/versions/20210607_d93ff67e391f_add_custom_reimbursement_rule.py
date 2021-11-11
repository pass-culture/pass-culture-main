"""Add `custom_reimbursement_rule` table

Revision ID: d93ff67e391f
Revises: e5cda043c0ee
Create Date: 2021-06-07 17:38:48.540828

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "d93ff67e391f"
down_revision = "e5cda043c0ee"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "custom_reimbursement_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=True),
        postgresql.ExcludeConstraint((sa.column("offerId"), "="), (sa.column("timespan"), "&&"), using="gist"),
        sa.CheckConstraint("lower(timespan) IS NOT NULL"),
        sa.ForeignKeyConstraint(
            ["offerId"],
            ["offer.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("custom_reimbursement_rule")
