"""clean_mediation_table

Revision ID: 2556f5577098
Revises: edb77d0140b7
Create Date: 2020-04-21 09:18:38.064455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2556f5577098'
down_revision = 'edb77d0140b7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DELETE FROM mediation WHERE "tutoIndex" IS NOT NULL;
        """)
    op.drop_column('mediation', 'tutoIndex')
    op.drop_column('mediation', 'frontText')
    op.drop_column('mediation', 'backText')
    op.alter_column('mediation', 'offerId', nullable=False)


def downgrade():
    op.alter_column('mediation', 'offerId', nullable=True)
    op.add_column('mediation', sa.Column('backText', sa.Text, nullable=True, index=True))
    op.add_column('mediation', sa.Column('frontText', sa.Text, nullable=True, index=True))
    op.add_column('mediation', sa.Column('tutoIndex', sa.Integer(), nullable=True, index=True))

