"""Add partial indexes on table "reaction" """

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9954d7d01119"
down_revision = "7bd20bc60b52"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade():
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_reaction_offer_like",
            "reaction",
            ["offerId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
            postgresql_where=sa.text('"reactionType" = \'LIKE\' AND "offerId" IS NOT NULL'),
        )
        op.create_index(
            "ix_reaction_product_like",
            "reaction",
            ["productId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
            postgresql_where=sa.text('"reactionType" = \'LIKE\' AND "productId" IS NOT NULL'),
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade():
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_reaction_offer_like",
            table_name="reaction",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            "ix_reaction_product_like",
            table_name="reaction",
            postgresql_concurrently=True,
            if_exists=True,
        )
