"""Create User Suspension foreign keys
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2a111d4feac2"
down_revision = "0d942b3261b7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "user_suspension_actorUserId_fkey", "user_suspension", "user", ["actorUserId"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "user_suspension_userId_fkey", "user_suspension", "user", ["userId"], ["id"], ondelete="CASCADE"
    )


def downgrade():
    op.drop_constraint("user_suspension_userId_fkey", "user_suspension", type_="foreignkey")
    op.drop_constraint("user_suspension_actorUserId_fkey", "user_suspension", type_="foreignkey")
