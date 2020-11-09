"""Changed column name from canBook to canBookFreeOffers. Added a constraint, cannot book free offers if admin

Revision ID: 7ce5154d87e2
Revises: e8c43e6dc0d8
Create Date: 2018-07-30 12:17:55.225619

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7ce5154d87e2'
down_revision = 'e8c43e6dc0d8'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'canBook', new_column_name='canBookFreeOffers')
    op.execute('UPDATE "user" SET "canBookFreeOffers"=False WHERE "isAdmin"=True;')
    op.create_check_constraint(constraint_name='check_admin_cannot_book_free_offers',
                               table_name='user',
                               condition='("canBookFreeOffers" IS FALSE AND "isAdmin" IS TRUE)'
                                     + 'OR ("isAdmin" IS FALSE)'
                               )


def downgrade():
    pass
