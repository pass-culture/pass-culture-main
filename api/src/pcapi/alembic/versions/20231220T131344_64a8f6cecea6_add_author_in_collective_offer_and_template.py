"""
add author in collective_offer and collective_offer_template
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "64a8f6cecea6"
down_revision = "d5e7a47d4991"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("authorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_authorId_fkey",
        "collective_offer",
        "user",
        ["authorId"],
        ["id"],
        postgresql_not_valid=True,
    )
    op.add_column("collective_offer_template", sa.Column("authorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_template_authorId_fkey",
        "collective_offer_template",
        "user",
        ["authorId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_template_authorId_fkey", "collective_offer_template", type_="foreignkey")
    op.drop_column("collective_offer_template", "authorId")
    op.drop_constraint("collective_offer_authorId_fkey", "collective_offer", type_="foreignkey")
    op.drop_column("collective_offer", "authorId")
