"""Create efficient unique index on "book_macro_section"."section" """

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bd42360a53c6"
down_revision = "984376b85d8e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """ CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "book_macro_section_section_idx" ON "book_macro_section" USING btree (lower("section")) """
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute(""" DROP INDEX CONCURRENTLY IF EXISTS "book_macro_section_section_idx" """)
    op.execute("BEGIN;")
