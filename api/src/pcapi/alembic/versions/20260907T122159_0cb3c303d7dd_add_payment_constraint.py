"""Add missing payment check constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0cb3c303d7dd"
down_revision = "2cfe1c7bcb34"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name="check_iban_and_bic_xor_not_iban_and_not_bic",
        table_name="payment",
        condition="(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="check_iban_and_bic_xor_not_iban_and_not_bic",
        table_name="payment",
        type_="check",
        if_exists=True,
    )
