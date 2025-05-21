"""Squash migrations - POST"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "54e6167683c9"
down_revision = "f460dc2c9f93"
branch_labels = ("post",)
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
