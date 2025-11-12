"""Change highlight timespan to datespan step 1 of 2
Change column type from tsrang to daterange

FIX: This migration needs to be performed in multiple steps.
     First, add the new *_datespan columns, then remove the *_timespan columns.
     This migration has already been applied in testing and staging.
     To avoid downtime in production, these two migrations are skipped, and a proper multi-step approach was used instead (see migrations 365ac49e50ae, 108c76ac8a3c and 99b8d179336d for reference).
"""

# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1b0355dabed"
down_revision = "3c967a1782c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(
    #     sa.text(
    #         """ALTER TABLE highlight ALTER COLUMN availability_timespan type daterange USING daterange(lower(availability_timespan)::date, upper(availability_timespan)::date);"""
    #     )
    # )
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(
    #     sa.text(
    #         """ALTER TABLE highlight ALTER COLUMN highlight_timespan type daterange USING daterange(lower(highlight_timespan)::date, upper(highlight_timespan)::date);"""
    #     )
    # )
    pass


def downgrade() -> None:
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(
    #     sa.text(
    #         """ALTER TABLE highlight ALTER COLUMN availability_timespan type tsrange USING tsrange(lower(availability_timespan)::date, upper(availability_timespan)::date);"""
    #     )
    # )
    # op.execute("select 1 -- squawk:ignore-next-statement")
    # op.execute(
    #     sa.text(
    #         """ALTER TABLE highlight ALTER COLUMN highlight_timespan type tsrange USING tsrange(lower(highlight_timespan)::date, upper(highlight_timespan)::date);"""
    #     )
    # )
    pass
