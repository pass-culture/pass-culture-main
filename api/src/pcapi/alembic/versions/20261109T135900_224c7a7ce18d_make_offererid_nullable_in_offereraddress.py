"""make_offererId_nullable_in_offereraddress"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "224c7a7ce18d"
down_revision = "8674a7978007"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer_address", "offererId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    pass
