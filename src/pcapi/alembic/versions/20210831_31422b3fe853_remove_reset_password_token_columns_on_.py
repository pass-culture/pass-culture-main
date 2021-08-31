"""remove_reset_password_token_columns_on_user

Revision ID: 31422b3fe853
Revises: af9c0fcd03e3
Create Date: 2021-08-31 14:42:58.963051

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "31422b3fe853"
down_revision = "af9c0fcd03e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("user", "resetPasswordToken")
    op.drop_column("user", "resetPasswordTokenValidityLimit")


def downgrade() -> None:
    op.add_column(
        "user", sa.Column("resetPasswordTokenValidityLimit", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
    )
    op.add_column("user", sa.Column("resetPasswordToken", sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.create_unique_constraint("user_resetPasswordToken_key", "user", ["resetPasswordToken"])
