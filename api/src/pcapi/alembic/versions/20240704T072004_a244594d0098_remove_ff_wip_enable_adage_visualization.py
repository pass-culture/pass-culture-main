"""
Remove the feature flag WIP_ENABLE_ADAGE_VISUALIZATION
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a244594d0098"
down_revision = "11a733e8b667"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_ADAGE_VISUALIZATION",
        isActive=True,
        description="Activer la nouvelle manière de visualiser les offres dans la recherche d'ADAGE.",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
