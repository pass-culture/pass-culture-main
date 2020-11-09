"""Add comment column on Venue

Revision ID: e0e5b8f53afd
Revises: 6b0fedcc7b6a
Create Date: 2018-10-16 15:24:40.682177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0e5b8f53afd'
down_revision = 'caafac8f5105'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue', sa.Column('comment', sa.TEXT, nullable=True))
    op.execute(
        """
        UPDATE venue
        SET comment = 'Merci de contacter l''équipe pass Culture pour lui communiquer le SIRET de ce lieu.'
        WHERE siret IS NULL
        AND "isVirtual" is FALSE;
        """
    )
    op.create_check_constraint(
        constraint_name='check_has_siret_xor_comment_xor_isVirtual',
        table_name='venue',
        condition="""
        (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
        OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
        OR (siret IS NOT NULL AND comment IS NULL AND "isVirtual" IS FALSE)
        """
    )


def downgrade():
    op.drop_constraint('check_has_siret_xor_comment_xor_isVirtual', 'venue')
    op.drop_column('venue', 'comment')
