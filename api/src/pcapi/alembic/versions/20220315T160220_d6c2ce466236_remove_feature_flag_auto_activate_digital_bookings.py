"""Remove AUTO_ACTIVATE_DIGITAL_BOOKINGS feature flag."""

# revision identifiers, used by Alembic.
revision = "d6c2ce466236"
down_revision = "162c8ddb055d"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="AUTO_ACTIVATE_DIGITAL_BOOKINGS",
        isActive=True,
        description="Activer (marquer comme utilisée) les réservations dès leur création pour les offres digitales",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
