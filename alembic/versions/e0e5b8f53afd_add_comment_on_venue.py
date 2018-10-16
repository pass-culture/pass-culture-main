"""Add comment column on Venue

Revision ID: e0e5b8f53afd
Revises: 6b0fedcc7b6a
Create Date: 2018-10-16 15:24:40.682177

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e0e5b8f53afd'
down_revision = '6b0fedcc7b6a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue', sa.Column('comment', sa.TEXT, nullable=True))
    op.create_check_constraint(
        constraint_name='check_has_siret_xor_comment_xor_isVirtual',
        table_name='venue',
        condition="""
        (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS NOT NULL)
        OR (siret IS NOT NULL AND comment IS NULL AND "isVirtual" IS NOT NULL)
        OR (siret IS NOT NULL AND comment IS NOT NULL AND "isVirtual" IS NULL)
        """
    )


def downgrade():
    op.drop_constraint('check_has_siret_xor_comment_xor_isVirtual', 'venue')
    op.drop_column('venue', 'comment')
test_pro_signup_should_create_user_offerer_digital_venue_and_userOfferer