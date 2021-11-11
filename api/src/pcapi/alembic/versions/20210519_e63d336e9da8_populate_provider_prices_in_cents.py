"""populate_provider_prices_in_cents

Revision ID: e63d336e9da8
Revises: e7a7fdd9c4e1
Create Date: 2021-05-19 14:05:25.182178

"""
from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "e63d336e9da8"
down_revision = "e7a7fdd9c4e1"
branch_labels = None
depends_on = None


def upgrade():
    statement = text('UPDATE provider SET "pricesInCents" = true WHERE name = :name')
    statement = statement.bindparams(name="TiteLive Stocks (Epagine / Place des libraires.com)")
    op.execute(statement)


def downgrade():
    pass
