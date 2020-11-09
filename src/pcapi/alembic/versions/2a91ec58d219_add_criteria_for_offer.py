"""add_criteria_for_offer

Revision ID: 2a91ec58d219
Revises: 7906543b4e96
Create Date: 2019-07-22 14:29:55.013272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a91ec58d219'
down_revision = '2920fd4ec916'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'criterion',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(140), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('scoreDelta', sa.Integer, nullable=False)
    )

    op.execute(
        '''
        INSERT INTO criterion (name, description, "scoreDelta")
        VALUES ('Bonne offre d\’appel', 'Offre déjà beaucoup réservée par les autres jeunes', 1);
        INSERT INTO criterion (name, description, "scoreDelta")
        VALUES ('Mauvaise accroche', 'Offre ne possèdant pas une accroche de qualité suffisante', -1);
        INSERT INTO criterion (name, description, "scoreDelta")
        VALUES ('Offre de médiation spécifique', 'Offre possédant une médiation orientée pour les jeunes de 18 ans', 2);
        '''
    )

    op.create_table(
        'offer_criterion',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('offerId', sa.BigInteger, nullable=False),
        sa.Column('criterionId', sa.BigInteger, nullable=False),
    )


def downgrade():
    op.drop_table('offer_criterion')
    op.drop_table('criterion')
