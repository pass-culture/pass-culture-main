"""
Validate constraints on reaction table (post deploy)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "11a733e8b667"
down_revision = "ac46cd60fe3f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE reaction VALIDATE CONSTRAINT "reaction_offerId_foreign_key" """)
    op.execute("""ALTER TABLE reaction VALIDATE CONSTRAINT "reaction_productId_foreign_key" """)
    op.execute("""ALTER TABLE reaction VALIDATE CONSTRAINT "reaction_userId_foreign_key" """)


def downgrade() -> None:
    pass
