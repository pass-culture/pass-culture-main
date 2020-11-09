"""Create table bank information

Revision ID: 4462a541eeed
Revises: 3f915af15e86
Create Date: 2019-02-11 13:15:00.695687

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey


revision = '4462a541eeed'
down_revision = 'dd92867bde82'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bank_information',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('offererId', sa.BigInteger, ForeignKey('offerer.id'), nullable=True),
        sa.Column('venueId', sa.BigInteger, ForeignKey('venue.id'), nullable=True),
        sa.Column('iban', sa.String(27), nullable=False),
        sa.Column('bic', sa.String(11), nullable=False),
        sa.Column('applicationId', sa.Integer, nullable=False),
        sa.Column('idAtProviders', sa.String(70), nullable=False, unique=True),
        sa.Column('dateModifiedAtLastProvider', sa.DateTime, nullable=True, default=datetime.utcnow),
        sa.Column('lastProviderId', sa.BigInteger, ForeignKey('provider.id'), nullable=True)
    )

    op.create_check_constraint(
        constraint_name='check_providable_with_provider_has_idatproviders',
        table_name='bank_information',
        condition='"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL'
    )


def downgrade():
    op.drop_table('bank_information')
