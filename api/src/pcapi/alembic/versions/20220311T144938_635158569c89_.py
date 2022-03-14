"""Remove gender column (use civility instead)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "635158569c89"
down_revision = "5c3a992204ff"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "gender")


def downgrade():
    op.add_column("user", sa.Column("gender", sa.VARCHAR(length=4), autoincrement=False, nullable=True))
