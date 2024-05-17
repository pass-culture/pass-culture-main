"""Make OffererAddress.label nullable
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2850f548b073"
down_revision = "73792a10a8f6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer_address", "label", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    # Nothing to downgrade
    # We won't make a column not nullable in downgrade migration
    pass
