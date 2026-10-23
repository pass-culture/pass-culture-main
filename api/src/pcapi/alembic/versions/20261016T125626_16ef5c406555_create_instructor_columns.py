"""Create instructorId columns for Offer, CollectiveOffer, CollectiveOfferTemplate"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "16ef5c406555"
down_revision = "e4a6d665249c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("instructorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_instructorId_fkey",
        "collective_offer",
        "user",
        ["instructorId"],
        ["id"],
        postgresql_not_valid=True,
    )

    op.add_column("collective_offer_template", sa.Column("instructorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_offer_template_instructorId_fkey",
        "collective_offer_template",
        "user",
        ["instructorId"],
        ["id"],
        postgresql_not_valid=True,
    )

    op.add_column("offer", sa.Column("instructorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "offer_instructorId_fkey",
        "offer",
        "user",
        ["instructorId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_column("collective_offer", "instructorId")
    op.drop_column("collective_offer_template", "instructorId")
    op.drop_column("offer", "instructorId")
