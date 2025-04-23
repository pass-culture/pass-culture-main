"""Make Address.inseeCode nullable"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1f3bc7f32c9f"
down_revision = "27635b8ff5c1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("address", "inseeCode", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    # We really don't want to make a column not nullable in a downgrade migration
    pass
