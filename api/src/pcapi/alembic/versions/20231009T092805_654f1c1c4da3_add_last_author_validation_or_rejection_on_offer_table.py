"""
add last author validation or rejection on "offer" table 1/2
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "654f1c1c4da3"
down_revision = "8347a72b24d0"
branch_labels = None
depends_on = None


FOREIGN_KEY_NAME = "offer_validation_author_fkey"
COLUMN_TO_ADD = "lastValidationAuthorUserId"


def upgrade() -> None:
    op.add_column("offer", sa.Column(COLUMN_TO_ADD, sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        FOREIGN_KEY_NAME,
        "offer",
        "user",
        [COLUMN_TO_ADD],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_column("offer", COLUMN_TO_ADD)
