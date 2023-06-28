"""
remove_feature_flag_enable_provider_authentification.py
"""


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "620bcd1b6630"
down_revision = "0c980fc6a68c"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_PROVIDER_AUTHENTIFICATION",
        isActive=False,  # <- adapter, selon la valeur actuelle du flag
        description="ajoute la possibilité selon is active ou non de faire l'authentification via le provider et non l'offerer",  #  <- adapter aussi
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
