"""Validate ondelete cascade on offerer offerer_address"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "984376b85d8e"
down_revision = "d1c087ca4219"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE "offerer_address" VALIDATE CONSTRAINT "offerer_address_offererId_fkey"')


def downgrade() -> None:
    pass
