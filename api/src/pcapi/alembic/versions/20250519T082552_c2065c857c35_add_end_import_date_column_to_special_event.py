"""add end_import_data column to special_event table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c2065c857c35"
down_revision = "b82597ef665d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("special_event", sa.Column("endImportDate", sa.Date(), nullable=True))
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_special_event_endImportDate"),
            "special_event",
            ["endImportDate"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_special_event_endImportDate"),
            table_name="special_event",
            if_exists=True,
            postgresql_concurrently=True,
        )

    op.drop_column("special_event", "endImportDate")
