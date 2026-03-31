"""for dev 3"""

from alembic import op
import sqlalchemy as sa

revision = 'ebba1a03bb14e9'
down_revision = None

def upgrade() -> None:
    op.add_column("booking", sa.Column("status", sa.Text(), nullable=True))
    op.drop_column("booking", "status")
    op.create_table("venue", sa.Column('id', sa.Integer(), nullable=False))
    op.drop_table("venue")
    op.rename_table("booking", 'booking_old')
    op.alter_column("booking", "price", type_=sa.Integer())

def downgrade() -> None:
    pass

