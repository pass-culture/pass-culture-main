"""add user email history table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b5eab9709bdd"
down_revision = "538cec694a7b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_email_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.Column("oldUserEmail", sa.String(length=120), nullable=False),
        sa.Column("oldDomainEmail", sa.String(length=120), nullable=False),
        sa.Column("newUserEmail", sa.String(length=120), nullable=False),
        sa.Column("newDomainEmail", sa.String(length=120), nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("eventType", sa.String(), nullable=False),
        sa.Column("deviceId", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_email_history_newDomainEmail"), "user_email_history", ["newDomainEmail"], unique=False
    )
    op.create_index(op.f("ix_user_email_history_newUserEmail"), "user_email_history", ["newUserEmail"], unique=False)
    op.create_index(
        op.f("ix_user_email_history_oldDomainEmail"), "user_email_history", ["oldDomainEmail"], unique=False
    )
    op.create_index(op.f("ix_user_email_history_oldUserEmail"), "user_email_history", ["oldUserEmail"], unique=False)
    op.create_index(op.f("ix_user_email_history_userId"), "user_email_history", ["userId"], unique=False)


def downgrade():
    op.drop_table("user_email_history")
