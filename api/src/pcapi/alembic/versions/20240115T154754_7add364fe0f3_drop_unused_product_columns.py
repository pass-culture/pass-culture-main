"""Drop unused product.isNational and product.url columns"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7add364fe0f3"
down_revision = "3467ee234047"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("product", "url")
    op.drop_column("product", "isNational")


def downgrade() -> None:
    op.add_column(
        "product",
        sa.Column("isNational", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
    op.add_column("product", sa.Column("url", sa.VARCHAR(length=255), autoincrement=False, nullable=True))
