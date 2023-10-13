"""
add last author validation or rejection on "collective_offer_template" table 1/2
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8347a72b24d0"
down_revision = "631df26e514b"
branch_labels = None
depends_on = None

FOREIGN_KEY_NAME = "collective_offer_template_validation_author_fkey"
COLUMN_TO_ADD = "lastValidationAuthorUserId"


def upgrade() -> None:
    op.add_column("collective_offer_template", sa.Column(COLUMN_TO_ADD, sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        FOREIGN_KEY_NAME,
        "collective_offer_template",
        "user",
        [COLUMN_TO_ADD],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_column("collective_offer_template", COLUMN_TO_ADD)
