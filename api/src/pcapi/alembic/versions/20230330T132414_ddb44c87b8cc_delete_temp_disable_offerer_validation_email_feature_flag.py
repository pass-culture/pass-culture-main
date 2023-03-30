"""delete TEMP_DISABLE_OFFERER_VALIDATION_EMAIL feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ddb44c87b8cc"
down_revision = "e53b1100dad0"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="TEMP_DISABLE_OFFERER_VALIDATION_EMAIL",
        isActive=False,
        description="Désactiver l'envoi d'email interne de validation par token pour les structures et rattachements",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
