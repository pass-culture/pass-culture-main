"""Remove WIP_ENABLE_ALLOCINE_TELERAMA_FESTIVAL_SPECIAL_PRICE feature flag."""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6b2fda23a359"
down_revision = "b2d77086bbd3"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_ALLOCINE_TELERAMA_FESTIVAL_SPECIAL_PRICE",
        isActive=True,
        description="Appliquer le tarif de 4€ pour les séances ciné concernées par le féstival Télérama",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
