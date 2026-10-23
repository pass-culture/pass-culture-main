"""Create favorite venues table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "23ced5c9120d"
down_revision = "e4a6d665249c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "favorite_venue",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "venueId", name="unique_user_venue_favorite"),
    )


def downgrade() -> None:
    op.drop_table("favorite_venue", if_exists=True)
