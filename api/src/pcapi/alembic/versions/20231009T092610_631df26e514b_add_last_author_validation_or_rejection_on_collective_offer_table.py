"""
add last author validation or rejection on "collective_offer" table 1/2
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "631df26e514b"
down_revision = "695bc13a7be4"
branch_labels = None
depends_on = None

FOREIGN_KEY_NAME = "collective_offer_validation_author_fkey"
COLUMN_TO_ADD = "lastValidationAuthorUserId"


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column(COLUMN_TO_ADD, sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        FOREIGN_KEY_NAME,
        "collective_offer",
        "user",
        [COLUMN_TO_ADD],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_column("collective_offer", COLUMN_TO_ADD)
