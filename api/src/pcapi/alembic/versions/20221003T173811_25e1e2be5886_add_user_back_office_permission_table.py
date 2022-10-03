"""add user_back_office_permission table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "25e1e2be5886"
down_revision = "246156d69d6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_back_office_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("permissionId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["permissionId"], ["permission.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "permissionId", name="unique_user_back_office_permission"),
    )
    op.create_index(
        op.f("ix_user_back_office_permission_userId"), "user_back_office_permission", ["userId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_back_office_permission_userId"), table_name="user_back_office_permission")
    op.drop_table("user_back_office_permission")
