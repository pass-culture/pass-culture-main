"""Add index on offer table with columns venueId, validation, publicationDatetime"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad37625d13c0"
down_revision = "9acd0f5ff379"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_offer_venueId_validation_publicationDatetime",
            "offer",
            ["venueId", "validation", "publicationDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_offer_venueId_validation_publicationDatetime",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
