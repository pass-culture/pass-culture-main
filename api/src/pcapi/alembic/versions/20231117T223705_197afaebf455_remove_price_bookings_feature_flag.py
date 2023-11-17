"""Remove PRICE_BOOKINGS feature flag"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "197afaebf455"
down_revision = "e0e253e1dca7"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="PRICE_BOOKINGS",
        isActive=False,
        description="Active la valorisation des réservations",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
