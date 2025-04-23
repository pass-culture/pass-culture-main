"""Add NOT NULL constraint on user_account_update_request."dsTechnicalId" (step 3 of 4)"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cc9a939003aa"
down_revision = "378a6eed6341"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("user_account_update_request", "dsTechnicalId", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("user_account_update_request", "dsTechnicalId", existing_type=sa.TEXT(), nullable=True)
