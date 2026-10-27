"""set_offererid_not_null_in_offereraddress"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0137ef79f2dc"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer_address", "offererId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    pass
