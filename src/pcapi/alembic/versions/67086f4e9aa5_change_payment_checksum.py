"""Change the type of the payment transaction checksum column

Revision ID: 67086f4e9aa5
Revises: b73fa4d77710
Create Date: 2019-01-02 14:41:54.932457

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '67086f4e9aa5'
down_revision = 'b73fa4d77710'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'payment_transaction', 'checksum',
        existing_type=sa.String(40),
        type_=sa.LargeBinary(32),
        existing_nullable=True,
        postgresql_using='checksum::bytea'
    )


def downgrade():
    op.alter_column(
        'payment_transaction', 'checksum',
        existing_type=sa.LargeBinary(32),
        type_=sa.String(40),
        existing_nullable=True
    )
