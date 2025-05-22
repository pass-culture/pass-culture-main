"""Add NOT NULL constraint on "special_event.endImportDate" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "08346141b0cc"
down_revision = "cb4aae091f35"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("special_event", "endImportDate", nullable=False)


def downgrade() -> None:
    op.alter_column("special_event", "endImportDate", nullable=True)
