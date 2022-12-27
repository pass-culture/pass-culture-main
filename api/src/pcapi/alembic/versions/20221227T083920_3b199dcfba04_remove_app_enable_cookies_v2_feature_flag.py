"""
Remove legacy APP_ENABLE_COOKIES_V2 feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3b199dcfba04"
down_revision = "2a2df641b70d"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="APP_ENABLE_COOKIES_V2",
        isActive=False,
        description="Activer la gestion conforme des cookies",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
