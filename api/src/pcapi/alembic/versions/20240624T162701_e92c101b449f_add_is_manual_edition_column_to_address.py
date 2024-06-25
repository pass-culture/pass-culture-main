"""add column: address."isManualEdition"
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e92c101b449f"
down_revision = "a07d08bb52cf"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("address", sa.Column("isManualEdition", sa.Boolean(), server_default=sa.text("false"), nullable=True))


def downgrade() -> None:
    op.drop_column("address", "isManualEdition")
