"""
Remove FF WIP_ENABLE_SATISFACTION_SURVEY
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8d5148b6b128"
down_revision = "3784f1bb8d9e"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_SATISFACTION_SURVEY",
        isActive=True,
        description="Activer l'affichage du questionnaire de satisfaction adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
