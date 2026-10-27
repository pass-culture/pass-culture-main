"""delete offererId from offerer_address"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "677f894d6dc9"
down_revision = "0137ef79f2dc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:

    op.drop_column("offerer_address", "offererId")


def downgrade() -> None:

    op.add_column("offerer_address", sa.Column("offererId", sa.BIGINT(), autoincrement=False, nullable=False))
