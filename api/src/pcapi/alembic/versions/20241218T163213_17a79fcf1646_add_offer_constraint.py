"""Add offer ean constraint."""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "17a79fcf1646"
down_revision = "b44dae2d1489"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_ean_validity",
        "offer",
        "ean ~ '^\\d{13}$'",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    pass
