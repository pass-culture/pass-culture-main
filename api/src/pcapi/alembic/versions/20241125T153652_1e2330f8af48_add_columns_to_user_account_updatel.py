"""Add columns to user_account_update_request table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.core.users import models as users_models
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1e2330f8af48"
down_revision = "cb98ffb241da"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("user_account_update_request", sa.Column("oldEmail", sa.Text(), nullable=True))
    op.add_column(
        "user_account_update_request",
        sa.Column(
            "updateTypes",
            postgresql.ARRAY(MagicEnum(users_models.UserAccountUpdateType)),
            server_default="{}",
            nullable=False,
        ),
    )
    op.add_column(
        "user_account_update_request",
        sa.Column(
            "flags",
            postgresql.ARRAY(MagicEnum(users_models.UserAccountUpdateFlag)),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_account_update_request", "flags")
    op.drop_column("user_account_update_request", "updateTypes")
    op.drop_column("user_account_update_request", "oldEmail")
