"""Add feature table

Revision ID: d4c38884d642
Revises: e945f921cc69
Create Date: 2019-03-13 15:05:49.681745

"""
from enum import Enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
class FeatureToggle(Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    DUO_OFFER = 'Permettre la réservation d’une offre pour soi et un accompagnant'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'

revision = 'd4c38884d642'
down_revision = 'e945f921cc69'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feature',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Enum(FeatureToggle), unique=True, nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('isActive', sa.Boolean, nullable=False, default=False)
    )

    op.execute(
        '''
        INSERT INTO feature (name, description, "isActive")
        VALUES ('WEBAPP_SIGNUP', 'webapp_signup', FALSE);
        '''
    )


def downgrade():
    op.drop_table('feature')
    op.execute('DROP TYPE FeatureToggle;')
