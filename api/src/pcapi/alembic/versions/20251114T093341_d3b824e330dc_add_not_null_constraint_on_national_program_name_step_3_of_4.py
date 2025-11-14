"""Add NOT NULL constraint on "national_program.name" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d3b824e330dc"
down_revision = "c4326429fbed"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("national_program", "name", nullable=False)


def downgrade() -> None:
    op.alter_column("national_program", "name", nullable=True)
