"""Add NOT NULL constraint on "collective_offer.formats" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f4b8b8892d3e"
down_revision = "d85e78eba5af"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_offer", "formats", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_offer", "formats", nullable=True)
