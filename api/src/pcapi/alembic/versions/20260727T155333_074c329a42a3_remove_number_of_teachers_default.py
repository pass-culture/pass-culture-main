"""Remove collective_stock numberOfTeachers default"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "074c329a42a3"
down_revision = "237683b365aa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "collective_stock", "numberOfTeachers", existing_type=sa.INTEGER(), server_default=None, existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "collective_stock",
        "numberOfTeachers",
        existing_type=sa.INTEGER(),
        server_default=sa.text("0"),
        existing_nullable=False,
    )
