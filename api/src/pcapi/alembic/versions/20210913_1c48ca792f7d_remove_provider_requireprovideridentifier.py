"""Remove Provider.requireProviderIdentifier
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c48ca792f7d"
down_revision = "e8e76a19c43c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("provider", "requireProviderIdentifier")


def downgrade():
    op.add_column(
        "provider",
        sa.Column(
            "requireProviderIdentifier",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=True,
        ),
    )
