"""Migrate booking table to hypertable"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c908437d34c0"
down_revision = "cf8ec83e521b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE booking DROP CONSTRAINT booking_pkey CASCADE;")
    op.execute("ALTER TABLE booking DROP CONSTRAINT booking_token_key;")

    op.execute("SELECT create_hypertable('booking', by_range('dateCreated', INTERVAL '1 day'), migrate_data => true);")

    op.execute('ALTER TABLE booking ADD PRIMARY KEY (id, "dateCreated");')
    op.execute('ALTER TABLE booking ADD CONSTRAINT booking_token_key UNIQUE (token, "dateCreated");')


def downgrade() -> None:
    op.execute("CREATE TABLE booking_regular AS TABLE booking;")
    op.execute("DROP TABLE booking;")
    op.execute("ALTER TABLE booking_regular RENAME TO booking;")

    op.execute("ALTER TABLE booking ADD CONSTRAINT booking_pkey PRIMARY KEY (id);")
    op.execute("ALTER TABLE booking ADD CONSTRAINT booking_token_key UNIQUE (token);")
