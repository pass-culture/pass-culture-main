"""Add venue_provider.dateCreated"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d02672d59311"
down_revision = "23e2d3b322ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "venue_provider", sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("venue_provider", "dateCreated")
