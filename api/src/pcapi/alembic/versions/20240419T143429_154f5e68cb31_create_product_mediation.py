"""
create product_mediation table that will store the image url of the product
"""

# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "154f5e68cb31"
down_revision = "d1767ee2dac1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
