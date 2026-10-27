"""Remove pro advice related columns and constraints"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9db2fe4f6198"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.drop_constraint("check_pro_advices_count_is_positive", table_name="product", if_exists=True)
    op.drop_column("product", "proAdvicesCount", if_exists=True)


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "product",
        sa.Column(
            "proAdvicesCount",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.execute(
        """ALTER TABLE "product" ADD CONSTRAINT "check_pro_advices_count_is_positive" CHECK ("proAdvicesCount" >= 0) NOT VALID"""
    )
