"""Squash migrations - PRE"""

# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c2065c857c35"
down_revision = "f460dc2c9f93"
branch_labels = ("pre",)
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
