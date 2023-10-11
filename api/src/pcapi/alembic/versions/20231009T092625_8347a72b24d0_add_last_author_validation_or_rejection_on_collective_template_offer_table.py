"""
add last author validation or rejection on "collective_offer_template" table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8347a72b24d0"
down_revision = "631df26e514b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer_template", sa.Column("lastValidationAuthorUserId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_template_validation_author_fkey",
        "collective_offer_template",
        "user",
        ["lastValidationAuthorUserId"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "collective_offer_template_validation_author_fkey", "collective_offer_template", type_="foreignkey"
    )
    op.drop_column("collective_offer_template", "lastValidationAuthorUserId")
