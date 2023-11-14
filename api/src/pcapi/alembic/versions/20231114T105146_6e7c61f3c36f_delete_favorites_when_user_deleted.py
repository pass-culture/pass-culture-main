"""Delete favorites when user is deleted 1/2
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6e7c61f3c36f"
down_revision = "997fff1573da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("favorite_userId_fkey", "favorite", type_="foreignkey")
    op.create_foreign_key(
        "favorite_userId_fkey", "favorite", "user", ["userId"], ["id"], ondelete="CASCADE", postgresql_not_valid=True
    )


def downgrade() -> None:
    op.drop_constraint("favorite_userId_fkey", "favorite", type_="foreignkey")
    op.create_foreign_key("favorite_userId_fkey", "favorite", "user", ["userId"], ["id"], postgresql_not_valid=True)
