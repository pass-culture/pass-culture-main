"""beneficiary_import_delete_old_fields

Revision ID: 0fce064a0f84
Revises: 31e0e5b920cf
Create Date: 2020-06-17 12:59:36.426445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fce064a0f84'
down_revision = '31e0e5b920cf'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('beneficiary_import', 'applicationId', nullable=False)
    op.alter_column('beneficiary_import', 'source', nullable=False)

    op.drop_constraint('uniq_beneficiary_import_demarcheSimplifieeApplicationId', table_name='beneficiary_import')
    op.drop_column('beneficiary_import', 'demarcheSimplifieeApplicationId')
    op.drop_column('beneficiary_import', 'demarcheSimplifieeProcedureId')

    op.drop_index('idx_beneficiary_import_application', table_name='beneficiary_import')

    op.execute('COMMIT')
    op.create_index(op.f('idx_beneficiary_import_application'),
        'beneficiary_import', ['applicationId', 'sourceId', 'source'],
        unique=True, postgresql_concurrently=True)


def downgrade():
    op.add_column('beneficiary_import', sa.Column('demarcheSimplifieeApplicationId', sa.BigInteger, nullable=False))
    op.add_column('beneficiary_import', sa.Column('demarcheSimplifieeProcedureId', sa.Integer, nullable=True))
    op.create_unique_constraint(
        'uniq_beneficiary_import_demarcheSimplifieeApplicationId', 'beneficiary_import', ['demarcheSimplifieeApplicationId']
    )

    op.alter_column('beneficiary_import', 'applicationId', nullable=True)
    op.alter_column('beneficiary_import', 'source', nullable=True)

    op.drop_index('idx_beneficiary_import_application', table_name='beneficiary_import')

    op.execute('COMMIT')
    op.create_index(op.f('idx_beneficiary_import_application'),
        'beneficiary_import', ['applicationId', 'sourceId', 'source'],
        postgresql_concurrently=True)
