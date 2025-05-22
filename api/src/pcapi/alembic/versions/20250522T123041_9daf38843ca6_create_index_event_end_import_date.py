"""create index on event.endImportDate"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9daf38843ca6"
down_revision = "ad5725a20f5e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
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
