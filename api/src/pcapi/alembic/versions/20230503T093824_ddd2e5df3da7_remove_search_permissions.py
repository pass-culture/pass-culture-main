"""Remove SEARCH_PUBLIC_ACCOUNT, REVIEW_PUBLIC_ACCOUNT, SEARCH_PRO_ACCOUNT, SEARCH_BOOKINGS permission"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ddd2e5df3da7"
down_revision = "25d6e15f465c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM permission WHERE name in ('SEARCH_PUBLIC_ACCOUNT', 'REVIEW_PUBLIC_ACCOUNT', 'SEARCH_PRO_ACCOUNT', 'SEARCH_BOOKINGS')"
    )


def downgrade() -> None:
    pass
