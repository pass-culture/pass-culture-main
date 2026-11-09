"""delete_offererid_in_offereraddress"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bd430f3db4bc"
down_revision = "07f33b4d4b2e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:

    op.drop_column("offerer_address", "offererId")


def downgrade() -> None:

    op.add_column("offerer_address", sa.Column("offererId", sa.BIGINT(), autoincrement=False, nullable=True))
