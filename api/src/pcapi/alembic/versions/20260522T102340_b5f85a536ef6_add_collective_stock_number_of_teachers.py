"""Add numberOfTeachers to collective_stock"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b5f85a536ef6"
down_revision = "e80ae38cef91"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # ignore prefer-bigint-over-int warning: the column is not supposed to contain large numbers
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "collective_stock", sa.Column("numberOfTeachers", sa.Integer(), server_default=sa.text("0"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("collective_stock", "numberOfTeachers")
