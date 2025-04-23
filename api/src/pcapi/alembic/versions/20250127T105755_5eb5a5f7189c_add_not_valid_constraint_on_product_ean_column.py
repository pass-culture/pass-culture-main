"""Add not valid check constraint on product ean column"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5eb5a5f7189c"
down_revision = "5450a88dc12b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_ean_validity",
        "product",
        "ean ~ '^\\d{13}$'",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("check_ean_validity", "product", "check")
