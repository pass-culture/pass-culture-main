"""Change max size of names on table user

Revision ID: bee8a14c1202
Revises: 2a91ec58d219
Create Date: 2019-07-24 15:02:28.628800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bee8a14c1202'
down_revision = '2a91ec58d219'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'firstName',
                    existing_type=sa.VARCHAR(length=35),
                    type_=sa.VARCHAR(length=128),
                    existing_nullable=True)

    op.alter_column('user', 'lastName',
                    existing_type=sa.VARCHAR(length=35),
                    type_=sa.VARCHAR(length=128),
                    existing_nullable=True)

    op.alter_column('user', 'publicName',
                    existing_type=sa.VARCHAR(length=100),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=False)


def downgrade():
    pass
