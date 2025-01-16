"""Add check_ean_validity constraint on product.ean"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "be7d24397ff7"
down_revision = "138018be9e5a"
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
    pass
