"""Add NOT NULL constraint on "educational_deposit.ministry" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bff3f0e86268"
down_revision = "4d9d26f546b5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("educational_deposit", "ministry", nullable=False)


def downgrade() -> None:
    op.alter_column("educational_deposit", "ministry", nullable=True)
