"""Add alternative text column to mediation table.
In order to be compliant with accessibility standards.
"""

import sqlalchemy as sa
from alembic import op


revision = "50df4d24f087"
down_revision = "48232008761a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("mediation", sa.Column("alternativeText", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("mediation", "alternativeText")
