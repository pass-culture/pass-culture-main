"""Add latitude and longitude to educational institution table."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "91ce430722b1"
down_revision = "ddf63ed44a81"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "educational_institution",
        sa.Column("latitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True),
    )
    op.add_column(
        "educational_institution",
        sa.Column("longitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("educational_institution", "longitude")
    op.drop_column("educational_institution", "latitude")
