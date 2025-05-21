"""Add indexes on offer.bookingAllowedDatetime & offer.publicationDatetime"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2d9c4b59ac7c"
down_revision = "54e6167683c9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_offer_bookingAllowedDatetime",
            "offer",
            ["bookingAllowedDatetime"],
            unique=False,
            if_not_exists=True,
            postgresql_where=sa.text('"bookingAllowedDatetime" IS NOT NULL'),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_offer_publicationDatetime",
            "offer",
            ["publicationDatetime"],
            unique=False,
            if_not_exists=True,
            postgresql_where=sa.text('"publicationDatetime" IS NOT NULL'),
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_offer_publicationDatetime",
            table_name="offer",
            if_exists=True,
            postgresql_where=sa.text('"publicationDatetime" IS NOT NULL'),
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_offer_bookingAllowedDatetime",
            table_name="offer",
            if_exists=True,
            postgresql_where=sa.text('"bookingAllowedDatetime" IS NOT NULL'),
            postgresql_concurrently=True,
        )
