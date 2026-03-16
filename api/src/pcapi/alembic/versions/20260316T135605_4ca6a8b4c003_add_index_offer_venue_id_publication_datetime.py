"""Add index on table offer for columns venueId and publicationDatetime"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4ca6a8b4c003"
down_revision = "4f7546074f71"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_offer_venueId_publicationDatetime",
            "offer",
            ["venueId", "publicationDatetime"],
            unique=False,
            postgresql_where='"publicationDatetime" IS NOT NULL',
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_offer_venueId_publicationDatetime",
            table_name="offer",
            postgresql_where='"publicationDatetime" IS NOT NULL',
            if_exists=True,
            postgresql_concurrently=True,
        )
