"""for dev 4"""

from alembic import op
import sqlalchemy as sa

revision = 'ebba1a03bb14e0'
down_revision = None

def upgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("email", sa.Text(), nullable=True))
        batch_op.drop_column("phone")
        batch_op.alter_column("email", type_=sa.Integer())

def downgrade() -> None:
    pass


