"""Add dateImported and dateValidated to settlement_batch"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "17c7dd953312"
down_revision = "fb2fd1a4a0cd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "settlement_batch", sa.Column("dateImported", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
    )
    op.add_column("settlement_batch", sa.Column("dateValidated", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("settlement_batch", "dateValidated")
    op.drop_column("settlement_batch", "dateImported")
