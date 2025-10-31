"""Add column to criterion table: highlightId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2b8eb6b584c3"
down_revision = "c23249637c33"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("criterion", sa.Column("highlightId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        op.f("criterion_highlightId_fkey"),
        "criterion",
        "highlight",
        ["highlightId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("criterion_highlightId_fkey", "criterion", type_="foreignkey")
    op.drop_column("criterion", "highlightId")
