"""Drop address columns in venue table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "438995923a1c"
down_revision = "3f2f6ae24d02"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "address")
    op.drop_column("venue", "banId")
    op.drop_column("venue", "departementCode")
    op.drop_column("venue", "timezone")
    op.drop_column("venue", "street")
    op.drop_column("venue", "longitude")
    op.drop_column("venue", "latitude")
    op.drop_column("venue", "postalCode")
    op.drop_column("venue", "city")


def downgrade() -> None:
    op.add_column("venue", sa.Column("city", sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("postalCode", sa.VARCHAR(length=6), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("latitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("longitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("street", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column(
        "venue",
        sa.Column(
            "timezone",
            sa.VARCHAR(length=50),
            server_default=sa.text("'Europe/Paris'::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column("venue", sa.Column("departementCode", sa.VARCHAR(length=3), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("banId", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("address", sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.create_index(op.f("ix_venue_departementCode"), "venue", ["departementCode"], unique=False)
