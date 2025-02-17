"""This is only to be sure that we don't write EAN in product.jsonData ever"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7f05525f7b5e"
down_revision = "6d08cf9b25c2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute("""ALTER TABLE product ADD CONSTRAINT check_no_ean_key CHECK (NOT ("jsonData" ? 'ean')); """)


def downgrade() -> None:
    pass
