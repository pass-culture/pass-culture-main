"""Add check constraint on reaction"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fec32ca73a57"
down_revision = "3a5ee54be21c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name="reaction_offer_product_check",
        table_name="reaction",
        condition='"offerId" IS NOT NULL AND "productId" IS NULL OR "productId" IS NOT NULL AND "offerId" IS NULL',
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="reaction_offer_product_check",
        table_name="reaction",
        type_="check",
        if_exists=True,
    )
