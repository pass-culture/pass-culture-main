"""Add "proAdvicesCount" column to "product" table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d0d19beab7b1"
down_revision = "5f21d2ca450e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.drop_constraint("check_pro_advices_count_is_positive", table_name="product")
    op.drop_column("product", "proAdvicesCount")
