"""Drop address columns in venue table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9a9d34c60788"
down_revision = "c57138342120"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "city")
    op.drop_column("venue", "timezone")
    op.drop_column("venue", "postalCode")
    op.drop_column("venue", "banId")
    op.drop_column("venue", "address")
    op.drop_column("venue", "street")


def downgrade() -> None:
    op.add_column("venue", sa.Column("street", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("address", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("banId", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("postalCode", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column(
        "venue",
        sa.Column(
            "timezone",
            sa.TEXT(),
            server_default=sa.text("'Europe/Paris'::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column("venue", sa.Column("city", sa.TEXT(), autoincrement=False, nullable=True))
