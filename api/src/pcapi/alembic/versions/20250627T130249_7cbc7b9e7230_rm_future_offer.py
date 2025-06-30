"""rm future_offer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7cbc7b9e7230"
down_revision = "ded99f0acd9e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("future_offer", if_exists=True)


def downgrade() -> None:
    op.create_table(
        "future_offer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("publicationDate", sa.DateTime(), nullable=False),
        sa.Column("isSoftDeleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_future_offer_offerId"),
            "future_offer",
            ["offerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_future_offer_publicationDate"),
            "future_offer",
            ["publicationDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
