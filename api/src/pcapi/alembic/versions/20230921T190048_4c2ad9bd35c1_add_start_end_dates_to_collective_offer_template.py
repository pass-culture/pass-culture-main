"""Add start/end dates to collective offer templates
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = '4c2ad9bd35c1'
down_revision = 'ef07f9582155'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('collective_offer_template', sa.Column('start', sa.DateTime(), nullable=True))
    op.add_column('collective_offer_template', sa.Column('end', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('collective_offer_template', 'end')
    op.drop_column('collective_offer_template', 'start')
