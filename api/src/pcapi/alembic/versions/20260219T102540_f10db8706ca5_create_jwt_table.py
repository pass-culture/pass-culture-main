"""create user_jwt table table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f10db8706ca5"
down_revision = "4fd267adeac8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "native_user_session",
        sa.Column("creationDatetime", sa.DateTime(), nullable=False),
        sa.Column("expirationDatetime", sa.DateTime(), nullable=False),
        sa.Column("refreshToken", sa.Text(), nullable=False),
        sa.Column("accessToken", sa.Text(), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("deviceId", sa.Text(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("accessToken"),
        sa.UniqueConstraint("refreshToken"),
    )


def downgrade() -> None:
    op.drop_table("native_user_session")
