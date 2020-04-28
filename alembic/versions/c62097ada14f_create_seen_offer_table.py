"""create_seen_offer_table

Revision ID: c62097ada14f
Revises: 2556f5577098
Create Date: 2020-04-10 13:51:57.162488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c62097ada14f'
down_revision = '2556f5577098'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'seen_offer',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('dateSeen', sa.DateTime, nullable=False),
        sa.Column('offerId', sa.BigInteger, nullable=False, index=True),
        sa.Column('userId', sa.BigInteger, nullable=False, index=True),
    )
    op.create_foreign_key(
        'seen_offer_offerId_fkey',
        'seen_offer', 'offer',
        ['offerId'], ['id'],
    )
    op.create_foreign_key(
        'seen_offer_userId_fkey',
        'seen_offer', 'user',
        ['userId'], ['id'],
    )


def downgrade():
    op.drop_constraint('seen_offer_offerId_fkey', 'seen_offer', type_='foreignkey')
    op.drop_constraint('seen_offer_userId_fkey', 'seen_offer', type_='foreignkey')
    op.drop_table('seen_offer')
