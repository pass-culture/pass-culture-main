"""
Drop UNIQUE constraint on externalProviderId
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "975f6274e3ce"
down_revision = "6f80f864d7ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE accessibility_provider DROP CONSTRAINT IF EXISTS make_accessibility_provider_unique")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint(
        "make_accessibility_provider_unique", "accessibility_provider", ["externalAccessibilityId"]
    )
