"""Add an optional direct offer link to work."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
revision = "73d81fa4c05b"
down_revision = "4ac83f712e61"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("work", sa.Column("offer_id", sa.BigInteger(), nullable=True))
    op.create_unique_constraint("work_offer_id_key", "work", ["offer_id"])
    op.create_foreign_key(
        "work_offer_id_fkey",
        "work",
        "offer",
        ["offer_id"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("work_offer_id_fkey", "work", type_="foreignkey")
    op.drop_constraint("work_offer_id_key", "work", type_="unique")
    op.drop_column("work", "offer_id")
