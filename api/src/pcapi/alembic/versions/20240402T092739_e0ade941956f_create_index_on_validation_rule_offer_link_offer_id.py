"""Create index on validation_rule_offer_link."offerId" """

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e0ade941956f"
down_revision = "a70801516cff"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_validation_rule_offer_link_offerId"),
            "validation_rule_offer_link",
            ["offerId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_validation_rule_offer_link_offerId"),
            table_name="validation_rule_offer_link",
            postgresql_concurrently=True,
            if_exists=True,
        )
