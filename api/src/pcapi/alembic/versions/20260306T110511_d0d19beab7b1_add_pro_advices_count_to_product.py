"""Add "proAdvicesCount" column to "product" table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d0d19beab7b1"
down_revision = "82cca698fb4f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product",
        sa.Column(
            "proAdvicesCount",
            sa.BigInteger,
            sa.CheckConstraint('"proAdvicesCount" >= 0', name="check_pro_advices_count_is_positive"),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("product", "proAdvicesCount")
