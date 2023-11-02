"""
Add `encryptedPassword` CGR column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "40dcae913a06"
down_revision = "389e0a92925f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cgr_cinema_details", sa.Column("encryptedPassword", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("cgr_cinema_details", "encryptedPassword")
