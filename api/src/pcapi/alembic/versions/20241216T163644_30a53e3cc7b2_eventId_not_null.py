"""Set eventId not nullable for table special_event_response"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "30a53e3cc7b2"
down_revision = "723ca088adc4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("special_event_response", "eventId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("special_event_response", "eventId", existing_type=sa.BIGINT(), nullable=True)
