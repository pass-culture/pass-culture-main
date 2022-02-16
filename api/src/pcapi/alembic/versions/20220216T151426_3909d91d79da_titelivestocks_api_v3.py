"""Upgrade TiteLive Stocks from API v2 to API v3
"""
from alembic import op
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "3909d91d79da"
down_revision = "2a111d4feac2"
branch_labels = None
depends_on = None


def upgrade():
    statement = text(
        "UPDATE provider "
        'SET "apiUrl" = \'https://api-stock.epagine.fr/v3/stocks\', "pricesInCents" = false '
        'WHERE "apiUrl" = :apiUrl'
    )
    statement = statement.bindparams(apiUrl="https://stockv2.epagine.fr/stocks")
    op.execute(statement)


def downgrade():
    statement = text(
        "UPDATE provider "
        'SET "apiUrl" = \'https://stockv2.epagine.fr/stocks\', "pricesInCents" = true '
        'WHERE "apiUrl" = :apiUrl'
    )
    statement = statement.bindparams(apiUrl="https://api-stock.epagine.fr/v3/stocks")
    op.execute(statement)
