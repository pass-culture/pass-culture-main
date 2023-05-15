"""create login device history table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "692bba538fb3"
down_revision = "f19414170fa5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_device_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("deviceId", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("os", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_login_device_history_deviceId"), "login_device_history", ["deviceId"], unique=False)
    op.create_index(op.f("ix_login_device_history_userId"), "login_device_history", ["userId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_login_device_history_userId"), table_name="login_device_history")
    op.drop_index(op.f("ix_login_device_history_deviceId"), table_name="login_device_history")
    op.drop_table("login_device_history")
