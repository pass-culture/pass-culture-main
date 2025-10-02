"""Remove creditRatio in educational_deposit"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e66cb8cfa231"
down_revision = "0799670439c7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("educational_deposit", "creditRatio")


def downgrade() -> None:
    op.add_column(
        "educational_deposit",
        sa.Column("creditRatio", sa.NUMERIC(precision=10, scale=3), autoincrement=False, nullable=True),
    )
