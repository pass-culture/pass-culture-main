"""Remove Venue's address fields
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "458b5c700a37"
down_revision = "d7e9a5af8f5d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "latitude")
    op.drop_column("venue", "banId")
    op.drop_column("venue", "address")
    op.drop_column("venue", "longitude")
    op.drop_column("venue", "city")
    op.drop_column("venue", "postalCode")
    op.drop_column("venue", "street")


def downgrade() -> None:
    op.add_column("venue", sa.Column("street", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("postalCode", sa.VARCHAR(length=6), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("city", sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("longitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("address", sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("banId", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("latitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
