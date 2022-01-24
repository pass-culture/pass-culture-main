"""remove_offer_idAtProviders_checks
"""
from alembic import op


revision = "1c78fd29dcf6"
down_revision = "f477748a5c40"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("offer_idAtProviders_key", "offer", type_="unique")
    op.drop_constraint("check_providable_with_provider_has_idatproviders", "offer", type_="check")
    op.create_check_constraint(
        "check_providable_with_provider_has_idatprovider",
        "offer",
        '"lastProviderId" IS NULL OR "idAtProvider" IS NOT NULL',
    )


def downgrade():
    op.create_unique_constraint("offer_idAtProviders_key", "offer", ["idAtProviders"])
    op.create_check_constraint(
        "check_providable_with_provider_has_idatproviders",
        "offer",
        '"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
    )
    op.drop_constraint("check_providable_with_provider_has_idatprovider", "offer", type_="check")
