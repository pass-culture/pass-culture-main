"""
Populate CGR `password` column with `encryptedPassword` values
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "997fff1573da"
down_revision = "c3eff57a0838"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""update cgr_cinema_details set password=cgr_cinema_details."encryptedPassword" """)


def downgrade() -> None:
    # Nothing to downgrade because:
    # - We already write encrypted values into password column
    # - We can’t know which values has been effectively updated in the upgrade step.
    pass
