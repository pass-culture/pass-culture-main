"""delete_old_finance_ffs
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "dab3016a1a39"
down_revision = "1c46cd3b225f"
branch_labels = None
depends_on = None


def get_enforce_bank_information_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENFORCE_BANK_INFORMATION_WITH_SIRET",
        isActive=False,
        description="Forcer les informations banquaires à être liées à un SIRET.",
    )


def get_new_bank_information_flag():
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NEW_BANK_INFORMATIONS_CREATION",
        isActive=True,
        description="Active le nouveau parcours d'ajout de coordonnées bancaires sur la page lieu",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_enforce_bank_information_flag())
    feature.remove_feature_from_database(get_new_bank_information_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_enforce_bank_information_flag())
    feature.add_feature_to_database(get_new_bank_information_flag())
