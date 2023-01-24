"""remove_ff_enable_new_booking_filters
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b2d77086bbd3"
down_revision = "06854dddfe34"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NEW_BOOKING_FILTERS",
        isActive=True,
        description="Active les nouveaux filtres sur les statuts pour la page de réservations",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
