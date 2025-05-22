"""
Add unicity constraint to AccessibilityProvider.venueId and externalAccessibilityProviderId
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5da6795c25fa"
down_revision = "4cc9e281e291"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_accessibility_provider_venueId", table_name="accessibility_provider")
    op.create_index(op.f("ix_accessibility_provider_venueId"), "accessibility_provider", ["venueId"], unique=True)
    op.create_unique_constraint(
        "make_accessibility_provider_unique", "accessibility_provider", ["externalAccessibilityId"]
    )


def downgrade() -> None:
    op.drop_constraint("make_accessibility_provider_unique", "accessibility_provider", type_="unique")
    op.drop_index(op.f("ix_accessibility_provider_venueId"), table_name="accessibility_provider")
    op.create_index("ix_accessibility_provider_venueId", "accessibility_provider", ["venueId"], unique=False)
