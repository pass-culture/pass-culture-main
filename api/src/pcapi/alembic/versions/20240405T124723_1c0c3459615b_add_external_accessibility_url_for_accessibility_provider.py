"""
Add column externalAccessibilityUrl on accessibility_provider table
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1c0c3459615b"
down_revision = "374e35815645"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("accessibility_provider", sa.Column("externalAccessibilityUrl", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("accessibility_provider", "externalAccessibilityUrl")
