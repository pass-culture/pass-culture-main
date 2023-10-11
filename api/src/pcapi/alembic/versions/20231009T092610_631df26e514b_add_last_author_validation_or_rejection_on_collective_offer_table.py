"""
add last author validation or rejection on "collective_offer" table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "631df26e514b"
down_revision = "695bc13a7be4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("lastValidationAuthorUserId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_validation_author_fkey",
        "collective_offer",
        "user",
        ["lastValidationAuthorUserId"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_validation_author_fkey", "collective_offer", type_="foreignkey")
    op.drop_column("collective_offer", "lastValidationAuthorUserId")
