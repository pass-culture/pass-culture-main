"""add triggers to version user

Revision ID: 565f79cfa5b2
Revises: cff9e82d0558
Create Date: 2019-05-28 07:03:16.612332

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '565f79cfa5b2'
down_revision = 'cff9e82d0558'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
    SELECT public.audit_table(oid, ARRAY['password', 'resetPasswordToken', 'validationToken']) 
    FROM pg_class 
    WHERE oid = 'user'::regclass;
    ''')


def downgrade():
    op.execute('''
    DROP TRIGGER audit_trigger_delete ON "user";
    DROP TRIGGER audit_trigger_insert ON "user";
    DROP TRIGGER audit_trigger_update ON "user";
    ''')
