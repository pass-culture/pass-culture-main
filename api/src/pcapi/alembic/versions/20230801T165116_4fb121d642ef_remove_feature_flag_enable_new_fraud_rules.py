"""
Remove feature flag WIP_ENABLE_NEW_FRAUD_RULES always at true
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4fb121d642ef"
down_revision = "48013aa5a395"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_FRAUD_RULES",
        isActive=True,
        description="Active la nouvelle gestion des règles de validation d'offre",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
