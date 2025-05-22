"""Add finalizationDatetime, publicationDatetime, bookingAllowedDatetime in offer table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "541fcbeb419e"
down_revision = "c2065c857c35"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("finalizationDatetime", sa.DateTime(), nullable=True))
    op.add_column("offer", sa.Column("publicationDatetime", sa.DateTime(), nullable=True))
    op.add_column("offer", sa.Column("bookingAllowedDatetime", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "bookingAllowedDatetime")
    op.drop_column("offer", "publicationDatetime")
    op.drop_column("offer", "finalizationDatetime")
