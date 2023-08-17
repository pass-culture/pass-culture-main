"""Delete obsolete table OfferValidationConfig
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0c980fc6a68c"
down_revision = "b93e190cb690"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP table if exists offer_validation_config")


def downgrade() -> None:
    pass  # there is no point in restoring the table
