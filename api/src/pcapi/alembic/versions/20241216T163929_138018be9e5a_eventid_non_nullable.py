"""Set eventId not nullable for table special_event_question"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "138018be9e5a"
down_revision = "30a53e3cc7b2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("special_event_question", "eventId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("special_event_question", "eventId", existing_type=sa.BIGINT(), nullable=True)
