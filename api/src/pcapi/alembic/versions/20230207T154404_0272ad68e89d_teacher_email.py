"""teacher_email
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0272ad68e89d"
down_revision = "d184cbdaadd5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("teacherEmail", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer", "teacherEmail")
