"""remove app enable category filter page feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "11cfe28f2708"
down_revision = "96d0426fabc4"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="APP_ENABLE_CATEGORY_FILTER_PAGE",
        isActive=False,
        description="Active le filtre des catégories dans les résultats de la recherche",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
