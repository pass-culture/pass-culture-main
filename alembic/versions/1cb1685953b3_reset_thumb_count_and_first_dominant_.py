"""reset_thumb_count_and_first_dominant_color_for_product

Revision ID: 1cb1685953b3
Revises: 621aad6436f9
Create Date: 2019-10-02 16:11:12.062353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cb1685953b3'
down_revision = '621aad6436f9'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    UPDATE product SET "thumbCount"=0, "firstThumbDominantColor"=NULL
    """)


def downgrade():
    pass
