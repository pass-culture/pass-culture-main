"""Validate check_ean_validity constraint on product.ean."""

from alembic import op
from sqlalchemy import text


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5509ff7c1d73"
down_revision = "be7d24397ff7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(text("""ALTER TABLE product VALIDATE CONSTRAINT "check_ean_validity";"""))


def downgrade() -> None:
    pass
