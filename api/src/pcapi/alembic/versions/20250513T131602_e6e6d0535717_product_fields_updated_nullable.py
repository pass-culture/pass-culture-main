"""Make product.fieldsUpdated nullable"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e6e6d0535717"
down_revision = "541fcbeb419e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("product", "fieldsUpdated", nullable=True)


def downgrade() -> None:
    # We wouldn't want to make it non nullable again
    pass
