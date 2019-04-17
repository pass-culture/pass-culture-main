"""empty message

Revision ID: d76f83432485
Revises: ddf0dc458d57
Create Date: 2019-04-17 12:30:10.303902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd76f83432485'
down_revision = 'ddf0dc458d57'
branch_labels = None
depends_on = None


def upgrade():
    CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL_NEW = """
        (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
        OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
        OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
    """
    op.drop_constraint('check_has_siret_xor_comment_xor_isVirtual', 'venue')
    op.create_check_constraint(constraint_name='check_has_siret_xor_comment_xor_isVirtual',
                               table_name='venue',
                               condition=CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL_NEW
                               )


def downgrade():
    CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL_OLD = """
        (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
        OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
        OR (siret IS NOT NULL AND comment IS NULL AND "isVirtual" IS FALSE)
    """
    op.drop_constraint('check_has_siret_xor_comment_xor_isVirtual', 'venue')
    op.create_check_constraint(constraint_name='check_has_siret_xor_comment_xor_isVirtual',
                               table_name='venue',
                               condition=CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL_OLD
                               )

