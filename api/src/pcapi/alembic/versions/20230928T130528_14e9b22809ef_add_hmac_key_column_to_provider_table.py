"""
Add hmac key column to provider table
This key will be used to sign the payload send to providers in charlie api
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "14e9b22809ef"
down_revision = "bdb5f7cdd367"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("provider", sa.Column("hmacKey", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("provider", "hmacKey")
