"""Create index on validation_rule_collective_offer_template_link.collectiveOfferTemplateId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8d1adabb3690"
down_revision = "34c3f6717826"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_validation_rule_collective_offer_template_link_collectiveOfferTemplateId"),
            "validation_rule_collective_offer_template_link",
            ["collectiveOfferTemplateId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_validation_rule_collective_offer_template_link_collectiveOfferTemplateId"),
            table_name="validation_rule_collective_offer_template_link",
            postgresql_concurrently=True,
            if_exists=True,
        )
