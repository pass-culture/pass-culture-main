"""delete_first_dominant_color

Revision ID: 002abca6d04e
Revises: 67c265a4498b
Create Date: 2019-11-21 13:01:18.463869

"""
from alembic import op

# revision identifiers, used by Alembic.

revision = '002abca6d04e'
down_revision = '67c265a4498b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('check_thumb_has_dominant_color', 'mediation')
    op.drop_constraint('check_thumb_has_dominant_color', 'product')
    op.drop_column('mediation', 'firstThumbDominantColor')
    op.drop_column('product', 'firstThumbDominantColor')


def downgrade():
    op.execute("""
        ALTER TABLE mediation
        ADD "firstThumbDominantColor" BYTEA DEFAULT 'b'\x00\x00\x00'' NOT NULL
    """)
    op.execute("""
        ALTER TABLE product
        ADD "firstThumbDominantColor" BYTEA DEFAULT 'b'\x00\x00\x00'' NOT NULL
    """)
    op.create_check_constraint(
        constraint_name='check_thumb_has_dominant_color',
        table_name='mediation',
        condition='"thumbCount"=0 OR "firstThumbDominantColor" IS NOT NULL'
    )
    op.create_check_constraint(
        constraint_name='check_thumb_has_dominant_color',
        table_name='product',
        condition='"thumbCount"=0 OR "firstThumbDominantColor" IS NOT NULL'
    )
