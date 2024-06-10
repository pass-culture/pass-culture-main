"""Validate the foreign key constraint on collective_offer_template.offererAddressId
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e6c2d152ff40"
down_revision = "5316ce0cc1dd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """ALTER TABLE collective_offer_template VALIDATE CONSTRAINT "collective_offer_template_offererAddressId_fkey" """
        )
    )


def downgrade() -> None:
    pass
