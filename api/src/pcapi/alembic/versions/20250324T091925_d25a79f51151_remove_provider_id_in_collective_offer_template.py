"""
Remove providerId in collective_offer_template
"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d25a79f51151"
down_revision = "01ecc63457be"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_collective_offer_template_providerId",
            table_name="collective_offer_template",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")

    op.drop_constraint("collectiveOfferTemplate_provider_fkey", "collective_offer_template", type_="foreignkey")
    op.drop_column("collective_offer_template", "providerId")


def downgrade() -> None:
    op.add_column("collective_offer_template", sa.Column("providerId", sa.BIGINT(), autoincrement=False, nullable=True))

    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_foreign_key(
        "collectiveOfferTemplate_provider_fkey", "collective_offer_template", "provider", ["providerId"], ["id"]
    )

    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_collective_offer_template_providerId",
            "collective_offer_template",
            ["providerId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
