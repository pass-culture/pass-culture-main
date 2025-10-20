"""Add NOT NULL constraint on "venue.publicName" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c214a734e583"
down_revision = "00275a31a11f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("venue", "publicName", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "publicName", nullable=True)
