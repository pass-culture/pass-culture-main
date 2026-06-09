"""create table event series"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "630a65525a87"
down_revision = "1a73b8c9a364"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_series",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mediationUuid", sa.Text(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "dateModified",
            sa.DateTime(),
            nullable=False,
            onupdate=sa.func.now(),
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("event_series", if_exists=True)
