"""drop_booking_recommandation_id_column

Revision ID: acbee9d1615b
Revises: 1196c69e1385
Create Date: 2021-01-15 14:09:43.264333

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "acbee9d1615b"
down_revision = "1196c69e1385"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("booking", "recommendationId")


def downgrade():
    op.create_foreign_key(None, "booking", "recommendation", ["recommendationId"], ["id"])
