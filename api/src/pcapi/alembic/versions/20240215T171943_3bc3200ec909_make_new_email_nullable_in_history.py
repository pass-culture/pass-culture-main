"""Make user email history new email nullable."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3bc3200ec909"
down_revision = "f54ee3618926"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user_email_history", "newUserEmail", existing_type=sa.VARCHAR(length=120), nullable=True)
    op.alter_column("user_email_history", "newDomainEmail", existing_type=sa.VARCHAR(length=120), nullable=True)


def downgrade() -> None:
    op.alter_column("user_email_history", "newDomainEmail", existing_type=sa.VARCHAR(length=120), nullable=False)
    op.alter_column("user_email_history", "newUserEmail", existing_type=sa.VARCHAR(length=120), nullable=False)
