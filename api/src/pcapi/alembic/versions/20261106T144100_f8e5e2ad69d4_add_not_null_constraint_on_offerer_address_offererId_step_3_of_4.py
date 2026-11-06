"""Add NOT NULL constraint on "offerer_address.offererId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = 'f8e5e2ad69d4'
down_revision = '2b8c01f25441'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer_address", "offererId", nullable=False)


def downgrade() -> None:
    op.alter_column("offerer_address", "offererId", nullable=True)
