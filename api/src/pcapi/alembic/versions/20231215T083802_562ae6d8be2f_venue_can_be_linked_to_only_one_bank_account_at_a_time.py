"""Add constraint on venue_bank_account_link venue can have only one bank account at same time"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "562ae6d8be2f"
down_revision = "2e521822e92a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("venue_bank_account_link_venueId_bankAccountId_timespan_excl", "venue_bank_account_link")
    op.create_exclude_constraint(
        "venue_bank_account_link_venueId_timespan_excl", "venue_bank_account_link", ("venueId", "="), ("timespan", "&&")
    )


def downgrade() -> None:
    op.drop_constraint("venue_bank_account_link_venueId_timespan_excl", "venue_bank_account_link")
    op.create_exclude_constraint(
        "venue_bank_account_link_venueId_bankAccountId_timespan_excl",
        "venue_bank_account_link",
        ("venueId", "="),
        ("bankAccountId", "="),
        ("timespan", "&&"),
    )
