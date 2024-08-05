"""Remove WIP_GOOGLE_MAPS_VENUE_IMAGES feature flag."""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4bd28b6d5d6c"
down_revision = "7ed9516f7af7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_GOOGLE_MAPS_VENUE_IMAGES",
        isActive=True,
        description="Utilise le modèle VenuePricingPointLink pour la valorisation",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
