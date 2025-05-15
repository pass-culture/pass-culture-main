"""
add AccessibilityProvider table in offerers models
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ca50ad3c3fd6"
down_revision = "b429bc5435d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accessibility_provider",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("externalAccessibilityId", sa.Text(), nullable=True),
        sa.Column("externalAccessibilityData", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("lastUpdateAtProvider", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accessibility_provider_venueId"), "accessibility_provider", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_accessibility_provider_venueId"), table_name="accessibility_provider")
    op.drop_table("accessibility_provider")
