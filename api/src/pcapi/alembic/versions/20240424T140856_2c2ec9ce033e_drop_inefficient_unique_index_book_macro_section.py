"""Drop inefficient index on "book_macro_section"."section" """

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2c2ec9ce033e"
down_revision = "bd42360a53c6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(""" ALTER TABLE "book_macro_section" DROP CONSTRAINT "book_macro_section_section_key" """)


def downgrade() -> None:
    # We can safely ignore the ADD CONSTRAINT statement because:
    # - we will never downgrade that migration
    # - even if we have to, it will be really fast as the table has few lines
    # - finally we can't mix DROP CONSTRAINT statement in the upgrade and CREATE UNIQUE INDEX in the downgrade
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute("""ALTER TABLE "book_macro_section" ADD CONSTRAINT book_macro_section_section_key UNIQUE ("section") """)
