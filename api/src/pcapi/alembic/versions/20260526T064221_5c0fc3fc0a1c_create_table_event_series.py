"""create table event series"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5c0fc3fc0a1c"
down_revision = "fdf1bb1a7de5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_series",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mediation_uuid", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modified", sa.DateTime(), nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("event_series", if_exists=True)
