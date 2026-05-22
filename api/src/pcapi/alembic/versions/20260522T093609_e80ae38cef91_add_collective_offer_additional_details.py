"""Add additionalDetails to collective_offer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e80ae38cef91"
down_revision = "f37686c3d4ed"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("additionalDetails", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer", "additionalDetails")
