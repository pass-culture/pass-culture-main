"""Create User Suspension Table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4e4384ac4c8f"
down_revision = "e6b4ede78bb3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_suspension",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("eventType", sa.String(), nullable=False),
        sa.Column("eventDate", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("actorUserId", sa.BigInteger(), nullable=True),
        sa.Column("reasonCode", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_suspension_userId"), "user_suspension", ["userId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_suspension_userId"), table_name="user_suspension")
    op.drop_table("user_suspension")
