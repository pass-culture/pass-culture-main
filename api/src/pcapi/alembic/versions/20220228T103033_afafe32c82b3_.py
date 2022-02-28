"""create gender and married_name columns
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "afafe32c82b3"
down_revision = "3dfc18c758cf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("gender", sa.String(length=4), nullable=True))
    op.add_column("user", sa.Column("married_name", sa.String(length=128), nullable=True))


def downgrade():
    op.drop_column("user", "married_name")
    op.drop_column("user", "gender")
