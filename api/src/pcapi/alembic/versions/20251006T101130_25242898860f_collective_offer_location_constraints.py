"""Add two contraints on collective_offer location fields"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "25242898860f"
down_revision = "5376ec9dfdf6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name="collective_offer_location_type_and_address_constraint",
        table_name="collective_offer",
        condition='("locationType" = \'ADDRESS\' AND "offererAddressId" IS NOT NULL) OR ("locationType" != \'ADDRESS\' AND "offererAddressId" IS NULL)',
        postgresql_not_valid=True,
    )
    op.create_check_constraint(
        constraint_name="collective_offer_location_type_and_comment_constraint",
        table_name="collective_offer",
        condition='"locationType" = \'TO_BE_DEFINED\' OR "locationComment" IS NULL',
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="collective_offer_location_type_and_address_constraint",
        table_name="collective_offer",
        type_="check",
        if_exists=True,
    )
    op.drop_constraint(
        constraint_name="collective_offer_location_type_and_comment_constraint",
        table_name="collective_offer",
        type_="check",
        if_exists=True,
    )
