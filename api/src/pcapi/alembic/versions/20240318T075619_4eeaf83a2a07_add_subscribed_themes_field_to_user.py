"""
add subscribed_themes field to notificationSubscriptions column in user table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4eeaf83a2a07"
down_revision = "b1c9eff03366"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "user",
        "notificationSubscriptions",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        server_default='{"marketing_push": true, "marketing_email": true, "subscribed_themes": []}',
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "user",
        "notificationSubscriptions",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        server_default=sa.text('\'{"marketing_push": true, "marketing_email": true}\'::jsonb'),
        existing_nullable=True,
    )
