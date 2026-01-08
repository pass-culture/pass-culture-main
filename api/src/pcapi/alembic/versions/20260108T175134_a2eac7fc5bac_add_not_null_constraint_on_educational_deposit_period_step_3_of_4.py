"""Add NOT NULL constraint on "educational_deposit.period" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a2eac7fc5bac"
down_revision = "d89009cfc2d2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("educational_deposit", "period", nullable=False)


def downgrade() -> None:
    op.alter_column("educational_deposit", "period", nullable=True)
