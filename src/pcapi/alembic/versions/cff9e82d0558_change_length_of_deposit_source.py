"""Change length of Deposit.source column

Revision ID: cff9e82d0558
Revises: f98d8cea0564
Create Date: 2019-05-21 13:49:08.219046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cff9e82d0558'
down_revision = 'f98d8cea0564'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'deposit', 'source',
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=300),
        existing_nullable=False
    )

    op.execute("""
    UPDATE deposit
    SET source = 'import par fichier CSV'
    WHERE source = 'activation';
    """)


def downgrade():
    op.execute("""
    UPDATE deposit
    SET source = 'activation'
    WHERE source = 'import par fichier CSV';
    """)

    op.alter_column(
        'deposit', 'source',
        existing_type=sa.VARCHAR(length=300),
        type_=sa.String(length=12),
        existing_nullable=False
    )
