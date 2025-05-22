"""Add NOT NULL constraint on "offerer.siren" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "57751e8826f0"
down_revision = "080d052208f3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer", "siren", nullable=False)


def downgrade() -> None:
    op.alter_column("offerer", "siren", nullable=True)
