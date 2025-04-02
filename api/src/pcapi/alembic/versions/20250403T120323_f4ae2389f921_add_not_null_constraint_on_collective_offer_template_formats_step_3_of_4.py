"""Add NOT NULL constraint on "collective_offer_template.formats" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f4ae2389f921"
down_revision = "7c21c3cb1b98"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_offer_template", "formats", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_offer_template", "formats", nullable=True)
