"""
Remove WIP_ENABLE_COLLECTIVE_DMS_TRACKING feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "38d84c4d6248"
down_revision = "49e118a9dd48"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_COLLECTIVE_DMS_TRACKING",
        isActive=True,
        description="Active le suivi du référencement DMS pour les acteurs EAC",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
