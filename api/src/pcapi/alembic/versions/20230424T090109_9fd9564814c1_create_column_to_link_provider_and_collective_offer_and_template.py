"""create column to link provider and collective offer and template
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9fd9564814c1"
down_revision = "298d82d25d41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("providerId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_collective_offer_providerId"), "collective_offer", ["providerId"], unique=False)
    op.create_foreign_key("collectiveOffer_provider_fkey", "collective_offer", "provider", ["providerId"], ["id"])
    op.add_column("collective_offer_template", sa.Column("providerId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_collective_offer_template_providerId"), "collective_offer_template", ["providerId"], unique=False
    )
    op.create_foreign_key(
        "collectiveOfferTemplate_provider_fkey", "collective_offer_template", "provider", ["providerId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("collectiveOfferTemplate_provider_fkey", "collective_offer_template", type_="foreignkey")
    op.drop_index(op.f("ix_collective_offer_template_providerId"), table_name="collective_offer_template")
    op.drop_column("collective_offer_template", "providerId")
    op.drop_constraint("collectiveOffer_provider_fkey", "collective_offer", type_="foreignkey")
    op.drop_index(op.f("ix_collective_offer_providerId"), table_name="collective_offer")
    op.drop_column("collective_offer", "providerId")
