"""Remove ENABLE_ACTIVATION_CODES feature flag."""

# revision identifiers, used by Alembic.
revision = "162c8ddb055d"
down_revision = "635158569c89"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_ACTIVATION_CODES",
        isActive=True,
        description="Permet la création de codes d'activation",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
