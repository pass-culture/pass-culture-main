"""Change highlight timespan to datespan step 2 of 2
Rename colums from timespan to datespan

FIX: This migration needs to be performed in multiple steps.
     First, add the new *_datespan columns, then remove the *_timespan columns.
     This migration has already been applied in testing and staging.
     To avoid downtime in production, these two migrations are skipped, and a proper multi-step approach was used instead (see migrations 365ac49e50ae, 108c76ac8a3c and 99b8d179336d for reference).
"""

# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a0188d242bcf"
down_revision = "b1b0355dabed"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN availability_timespan TO availability_datespan;"""))
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN highlight_timespan TO highlight_datespan;"""))
    pass


def downgrade() -> None:
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN availability_datespan TO availability_timespan;"""))
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN highlight_datespan TO highlight_timespan;"""))
    pass
