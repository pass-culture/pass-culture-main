"""Add NOT NULL constraint on "highlight.highlight_datespan" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6aeccdd21eeb"
down_revision = "7eeefa6d3961"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("highlight", "highlight_datespan", nullable=False)


def downgrade() -> None:
    op.alter_column("highlight", "highlight_datespan", nullable=True)
