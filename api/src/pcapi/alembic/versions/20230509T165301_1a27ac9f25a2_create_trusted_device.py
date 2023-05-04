"""create trusted device table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1a27ac9f25a2"
down_revision = "ddd0895ce8c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trusted_device",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("deviceId", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("os", sa.Text(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trusted_device_deviceId"), "trusted_device", ["deviceId"], unique=False)
    op.create_index(op.f("ix_trusted_device_userId"), "trusted_device", ["userId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trusted_device_userId"), table_name="trusted_device")
    op.drop_index(op.f("ix_trusted_device_deviceId"), table_name="trusted_device")
    op.drop_table("trusted_device")
