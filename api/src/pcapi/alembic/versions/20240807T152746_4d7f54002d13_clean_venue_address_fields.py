"""Remove Venue's address fields
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4d7f54002d13"
down_revision = "35d67a2cddcd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "city")
    op.drop_column("venue", "street")
    op.drop_column("venue", "address")
    op.drop_column("venue", "postalCode")
    op.drop_column("venue", "timezone")
    op.drop_column("venue", "banId")


def downgrade() -> None:
    op.add_column("venue", sa.Column("banId", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column(
        "venue",
        sa.Column(
            "timezone",
            sa.VARCHAR(length=50),
            server_default=sa.text("'Europe/Paris'::character varying"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column("venue", sa.Column("postalCode", sa.VARCHAR(length=6), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("address", sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("street", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("city", sa.VARCHAR(length=50), autoincrement=False, nullable=True))
