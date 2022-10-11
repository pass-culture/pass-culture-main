"""add backoffice_user_profile table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3a90f34b5b14"
down_revision = "e3caccc345ea"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "backoffice_user_profile",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backoffice_user_profile_userId"), "backoffice_user_profile", ["userId"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_backoffice_user_profile_userId"), table_name="backoffice_user_profile")
    op.drop_table("backoffice_user_profile")
