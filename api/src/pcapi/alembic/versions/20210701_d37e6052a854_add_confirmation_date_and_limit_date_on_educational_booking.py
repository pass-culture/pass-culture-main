"""add_confirmation_date_and_limit_date_on_educational_booking

Revision ID: d37e6052a854
Revises: 5ac75d2310d0
Create Date: 2021-07-01 08:23:56.538045

"""
from alembic import op
import sqlalchemy as sa


revision = "d37e6052a854"
down_revision = "5ac75d2310d0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("educational_booking", sa.Column("confirmationDate", sa.DateTime(), nullable=True))
    op.add_column("educational_booking", sa.Column("confirmationLimitDate", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("educational_booking", "confirmationLimitDate")
    op.drop_column("educational_booking", "confirmationDate")
