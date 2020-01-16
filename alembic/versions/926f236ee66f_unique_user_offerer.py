"""unique_user_offerer

Revision ID: 926f236ee66f
Revises: 035f0ee8ea70
Create Date: 2019-07-01 11:07:35.973292

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '926f236ee66f'
down_revision = '035f0ee8ea70'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'unique_user_offerer', 'user_offerer', ['userId', 'offererId']
    )


def downgrade():
    op.drop_constraint('unique_user_offerer', 'user_offerer')
