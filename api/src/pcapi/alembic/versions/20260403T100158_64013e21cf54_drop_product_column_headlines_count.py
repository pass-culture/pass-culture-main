"""drop product column headlinesCount"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "64013e21cf54"
down_revision = "3d56fe5bbe15"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product", "headlinesCount")


def downgrade() -> None:
    op.add_column(
        "product",
        sa.Column(
            "headlinesCount",
            sa.BigInteger,
            sa.CheckConstraint('"headlinesCount" >= 0', name="check_headlines_count_is_positive"),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
