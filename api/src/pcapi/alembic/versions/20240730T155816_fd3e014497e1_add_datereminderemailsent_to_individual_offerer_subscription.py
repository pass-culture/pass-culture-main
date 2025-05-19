"""Add dateReminderEmailSent to IndivdualOffererSubscription"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fd3e014497e1"
down_revision = "a838739fcc02"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("individual_offerer_subscription", sa.Column("dateReminderEmailSent", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("individual_offerer_subscription", "dateReminderEmailSent")
