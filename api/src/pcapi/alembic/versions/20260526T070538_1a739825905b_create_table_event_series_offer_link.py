"""create table event series offer link"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1a739825905b"
down_revision = "fdf1bb1a7de5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_series_offer_link",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("event_series_id", sa.Text(), nullable=False),
        sa.Column("offer_id", sa.BigInteger(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modified", sa.DateTime(), nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["event_series_id"], ["event_series.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["offer_id"], ["offer.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("offer_id", name="unique_offer_id_constraint"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("event_series_offer_link", if_exists=True)
