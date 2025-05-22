"""Drop CollectiveOfferEducationalRedactor"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6de6b0acf802"
down_revision = "c34443975234"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("collective_offer_educational_redactor")


def downgrade() -> None:
    op.create_table(
        "collective_offer_educational_redactor",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalRedactorId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["educationalRedactorId"], ["educational_redactor.id"]),
        sa.ForeignKeyConstraint(["collectiveOfferId"], ["collective_offer.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalRedactorId", "collectiveOfferId", name="unique_redactorId_offer"),
    )
