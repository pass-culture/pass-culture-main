"""Creation of index for CollectiveOfferTemplate.OffererAddressId
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "06ecb5800626"
down_revision = "ff36979aea69"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_collective_offer_template_offererAddressId"),
            "collective_offer_template",
            ["offererAddressId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_offer_template_offererAddressId"),
            table_name="collective_offer_template",
            postgresql_concurrently=True,
            if_exists=True,
        )
