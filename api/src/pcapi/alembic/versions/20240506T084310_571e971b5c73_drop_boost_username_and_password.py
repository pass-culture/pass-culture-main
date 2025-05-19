"""Drop "username" & "password" columns from "boost_cinema_details" table."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "571e971b5c73"
down_revision = "b40706d45035"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("boost_cinema_details", "password")
    op.drop_column("boost_cinema_details", "username")


def downgrade() -> None:
    op.add_column("boost_cinema_details", sa.Column("username", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("boost_cinema_details", sa.Column("password", sa.TEXT(), autoincrement=False, nullable=True))
