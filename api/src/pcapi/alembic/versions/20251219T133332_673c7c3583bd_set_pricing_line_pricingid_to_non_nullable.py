"""set PricingLine pricingId to non-nullable"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "673c7c3583bd"
down_revision = "261a8504ec57"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("pricing_line", "pricingId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("pricing_line", "pricingId", existing_type=sa.BIGINT(), nullable=True)
