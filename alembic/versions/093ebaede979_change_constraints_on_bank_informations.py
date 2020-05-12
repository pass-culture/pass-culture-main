"""change_constraints_on_bank_informations

Revision ID: 093ebaede979
Revises: 44d783e1c855
Create Date: 2020-05-11 15:08:32.330029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '093ebaede979'
down_revision = '44d783e1c855'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('idx_bank_information_applicationId'), 'bank_information', ['applicationId'], unique=True)
    op.alter_column(
        'bank_information', 'idAtProviders',
        nullable=True
    )

def downgrade():
    op.drop_index('idx_bank_information_applicationId', table_name='bank_information')
    op.alter_column(
        'bank_information', 'idAtProviders',
        nullable=False
    )
