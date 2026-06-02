"""create table event series offer link"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5dc3a149e8fa"
down_revision = "630a65525a87"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_series_offer_link",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("eventSeriesId", sa.Text(), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("dateModified", sa.DateTime(), nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["eventSeriesId"], ["event_series.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("offerId", name="unique_offer_id_constraint"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("event_series_offer_link", if_exists=True)
