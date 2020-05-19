"""add_missing_constraints_on_allocine_venue_provider_price_rule

Revision ID: 3a5629a53c17
Revises: 61fe7b7c5a31
Create Date: 2020-05-19 16:01:13.791090

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a5629a53c17'
down_revision = '61fe7b7c5a31'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('unique_venue_provider_price_rule', 'allocine_venue_provider_price_rule')
    op.create_unique_constraint(
        'unique_allocine_venue_provider_price_rule',
        'allocine_venue_provider_price_rule', ['allocineVenueProviderId', 'priceRule']
    )


def downgrade():
    op.drop_constraint('unique_allocine_venue_provider_price_rule', 'allocine_venue_provider_price_rule')
    op.create_unique_constraint(
        'unique_venue_provider_price_rule', 'allocine_venue_provider_price_rule', ['venueProviderId', 'priceRule']
    )
