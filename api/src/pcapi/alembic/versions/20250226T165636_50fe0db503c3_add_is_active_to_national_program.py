"""
Add isActive to national_program
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "50fe0db503c3"
down_revision = "9d1b6d3edf16"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "national_program", sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("national_program", "isActive")
