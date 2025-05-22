"""Delete INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4cc9e281e291"
down_revision = "2cc0a6822cf8"
branch_labels = None
depends_on = None


def get_flag():
    from pcapi.models import feature

    return feature.Feature(
        name="INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS",
        isActive=True,
        description="Inclure les anciens modèles de données pour le téléchargement des remboursements ",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
