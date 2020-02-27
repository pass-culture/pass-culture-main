"""create_iris_france_table

Revision ID: 3e44b9ad4478
Revises: 771cab29d46e
Create Date: 2020-02-25 18:30:52.946282

"""
import sqlalchemy as sa
from alembic import op
from geoalchemy2.types import Geometry

# revision identifiers, used by Alembic.
revision = '3e44b9ad4478'
down_revision = '771cab29d46e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'iris_france',
        sa.Column('irisCode', sa.VARCHAR(9), nullable=False),
        sa.Column('centroid', Geometry(geometry_type='POINT'), nullable=False),
        sa.Column('shape', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
    )


def downgrade():
    op.drop_table('iris_france')
