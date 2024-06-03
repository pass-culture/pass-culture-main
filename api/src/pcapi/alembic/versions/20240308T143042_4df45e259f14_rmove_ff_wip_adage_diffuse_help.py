"""
Remove FF WIP_ENABLE_DIFFUSE_HELP
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4df45e259f14"
down_revision = "8d5148b6b128"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_DIFFUSE_HELP",
        isActive=True,
        description="Activer l'affichage de l'aide diffuse adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
