"""validate offer_compliance constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7356bdbfd295"
down_revision = "cb92f6a2a755"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE offer_compliance VALIDATE CONSTRAINT "offer_compliance_offerId_fkey" """)


def downgrade() -> None:
    pass
