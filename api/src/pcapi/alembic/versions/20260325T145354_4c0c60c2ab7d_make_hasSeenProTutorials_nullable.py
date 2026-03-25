"""make hasSeenProTutorials nullable"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4c0c60c2ab7d"
down_revision = "17c7dd953312"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("user", "hasSeenProTutorials", nullable=True)


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("user", "hasSeenProTutorials", nullable=False)
