"""Delete production.url column (1/2)"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2b4a02b0a8d5"
down_revision = "1343aeafc182"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("product_mediation", "url", nullable=True)


def downgrade() -> None:
    # some rows might be empty do not make it un-nullable
    pass
