"""
Add venue_bank_account_link table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6ad1b6cb8328"
down_revision = "884b3016640c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "venue_bank_account_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=False),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=False),
        postgresql.ExcludeConstraint(
            (sa.column("venueId"), "="), (sa.column("bankAccountId"), "="), (sa.column("timespan"), "&&"), using="gist"
        ),
        sa.ForeignKeyConstraint(["bankAccountId"], ["bank_account.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_venue_bank_account_link_bankAccountId"), "venue_bank_account_link", ["bankAccountId"], unique=False
    )
    op.create_index(op.f("ix_venue_bank_account_link_venueId"), "venue_bank_account_link", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_table("venue_bank_account_link")
