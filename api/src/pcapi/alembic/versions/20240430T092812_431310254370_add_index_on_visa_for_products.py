"""Create index on extraData["visa"] for the table "Product" """

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "431310254370"
down_revision = "34a1a2acff4f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_product_visa",
            "product",
            [sa.text("(\"jsonData\" ->> 'visa')")],
            unique=True,
            postgresql_concurrently=True,
            postgresql_where=sa.text("(\"jsonData\" ->> 'visa') IS NOT NULL"),
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_product_visa",
            table_name="product",
            postgresql_concurrently=True,
            if_exists=True,
            postgresql_where=sa.text("(\"jsonData\" ->> 'visa') IS NOT NULL"),
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
