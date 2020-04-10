"""create_seen_offers_table

Revision ID: c62097ada14f
Revises: 2b6541bb0076
Create Date: 2020-04-10 13:51:57.162488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c62097ada14f'
down_revision = '2b6541bb0076'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'seen_offers',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('dateSeen', sa.BigInteger, nullable=False),
        sa.Column('offerId', sa.BigInteger, nullable=False, index=True),
        sa.Column('userId', sa.BigInteger, nullable=False, index=True),
    )
    op.create_foreign_key(
        'seen_offers_offerId_fkey',
        'seen_offers', 'offer',
        ['offerId'], ['id'],
    )
    op.create_foreign_key(
        'seen_offers_userId_fkey',
        'seen_offers', 'user',
        ['userId'], ['id'],
    )


def downgrade():
    op.drop_constraint('seen_offers_offerId_fkey', 'seen_offers', type_='foreignkey')
    op.drop_constraint('seen_offers_userId_fkey', 'seen_offers', type_='foreignkey')
    op.drop_table('iris_venues')