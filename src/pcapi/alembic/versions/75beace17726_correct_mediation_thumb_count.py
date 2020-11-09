"""empty message

Revision ID: 75beace17726
Revises: 284df157db6d
Create Date: 2019-09-04 13:32:19.160590

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '75beace17726'
down_revision = '284df157db6d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        UPDATE mediation SET "thumbCount" = 1 WHERE "tutoIndex"=0;
        UPDATE mediation SET "thumbCount" = 2 WHERE "tutoIndex"=1;
    ''')


def downgrade():
    pass
