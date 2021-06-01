"""Add Payment.batchDate (with an index)

Revision ID: 2a24a51d4735
Revises: 8bad2344ab11
Create Date: 2021-05-31 16:10:05.255571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a24a51d4735"
down_revision = "32bea863ac77"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("payment", sa.Column("batchDate", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_payment_batchDate"), "payment", ["batchDate"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_payment_batchDate"), table_name="payment")
    op.drop_column("payment", "batchDate")
