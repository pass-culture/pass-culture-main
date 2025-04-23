"""Set accessibility_provider.externalAccessibilityId and externalAccessibilityUrl not nullable"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2a3cbc3aa996"
down_revision = "257bb3c980a7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("accessibility_provider", "externalAccessibilityId", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("accessibility_provider", "externalAccessibilityUrl", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("accessibility_provider", "externalAccessibilityUrl", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("accessibility_provider", "externalAccessibilityId", existing_type=sa.TEXT(), nullable=True)
