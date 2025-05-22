"""Add NOT NULL constraint on "finance_incident.origin" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e7310a92efcf"
down_revision = "84f53732b4c7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("finance_incident", "origin", nullable=False)


def downgrade() -> None:
    op.alter_column("finance_incident", "origin", nullable=True)
