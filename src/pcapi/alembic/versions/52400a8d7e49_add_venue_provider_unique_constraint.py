"""add_venue_provider_unique_constraint

Revision ID: 52400a8d7e49
Revises: e387ee2c380d
Create Date: 2019-11-07 10:11:39.716514

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '52400a8d7e49'
down_revision = 'e387ee2c380d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'unique_venue_provider', 'venue_provider', ['venueId', 'providerId', 'venueIdAtOfferProvider']
    )


def downgrade():
    op.drop_constraint('unique_venue_provider', 'venue_provider')
