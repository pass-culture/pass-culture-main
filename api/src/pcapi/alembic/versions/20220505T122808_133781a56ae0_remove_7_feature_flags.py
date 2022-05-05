"""remove_7_feature_flags
"""

# revision identifiers, used by Alembic.
revision = "133781a56ae0"
down_revision = "beaefcf60bc9"
branch_labels = None
depends_on = None


def get_flags() -> list:
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return [
        feature.Feature(
            name="ALLOW_IDCHECK_UNDERAGE_REGISTRATION",
            isActive=True,
            description="Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check",
        ),
        feature.Feature(
            name="ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE",
            isActive=True,
            description="Utiliser la nouvelle règle de détection d'utilisateur en doublon",
        ),
        feature.Feature(
            name="ENABLE_ID_CHECK_RETENTION",
            isActive=True,
            description="Active le mode bassin de retention dans Id Check V2",
        ),
        feature.Feature(
            name="ENABLE_NATIVE_APP_RECAPTCHA",
            isActive=True,
            description="Active le reCaptacha sur l'API native",
        ),
        feature.Feature(
            name="ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING",
            isActive=False,
            description="Active le mode debug Firebase pour l'Id Check intégrée à l'application native",
        ),
        feature.Feature(
            name="ENABLE_NATIVE_ID_CHECK_VERSION",
            isActive=True,
            description="Utilise la version d'ID-Check intégrée à l'application native",
        ),
        feature.Feature(
            name="WEBAPP_V2_ENABLED",
            isActive=True,
            description="Utiliser la nouvelle web app (décli web/v2) au lieu de l'ancienne",
        ),
    ]


def upgrade() -> None:
    from pcapi.models import feature

    for flag in get_flags():
        feature.remove_feature_from_database(flag)


def downgrade() -> None:
    from pcapi.models import feature

    for flag in get_flags():
        feature.add_feature_to_database(flag)
