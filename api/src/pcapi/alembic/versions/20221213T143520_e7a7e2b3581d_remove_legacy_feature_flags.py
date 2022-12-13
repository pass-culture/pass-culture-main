"""Remove legacy WEBAPP_V2_ENABLED feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e7a7e2b3581d"
down_revision = "99befb418b1f"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WEBAPP_V2_ENABLED",
        isActive=True,
        description="Utiliser la nouvelle web app (décli web/v2) au lieu de l'ancienne",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
