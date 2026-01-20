"""Add NOT NULL constraint on "user_session.expirationDatetime" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3d993db2a1f2"
down_revision = "50929da2d3c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("user_session", "expirationDatetime", nullable=False)


def downgrade() -> None:
    op.alter_column("user_session", "expirationDatetime", nullable=True)
