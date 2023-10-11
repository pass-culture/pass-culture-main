"""
add last author validation or rejection on "offer" table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "654f1c1c4da3"
down_revision = "8347a72b24d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("lastValidationAuthorUserId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "offer_validation_author_fkey",
        "offer",
        "user",
        ["lastValidationAuthorUserId"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("offer_validation_author_fkey", "offer", type_="foreignkey")
    op.drop_column("offer", "lastValidationAuthorUserId")
