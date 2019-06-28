"""Add feature table

Revision ID: d4c38884d642
Revises: e945f921cc69
Create Date: 2019-03-13 15:05:49.681745

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
from models.feature import FeatureToggle

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
