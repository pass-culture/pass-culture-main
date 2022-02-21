"""This migration used to add the `OFFER_VALIDATION_MOCK_COMPUTATION`
 feature flag, but it is no longer needed.

Revision ID: bd142e43ea07
Revises: 069e6621725a
Create Date: 2021-03-22 12:07:13.888217

"""


# revision identifiers, used by Alembic.
revision = "bd142e43ea07"
down_revision = "069e6621725a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
