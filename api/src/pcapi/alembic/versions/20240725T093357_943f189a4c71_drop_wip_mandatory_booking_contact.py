"""
Delete WIP_MANDATORY_BOOKING_CONTACT Feature Flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "943f189a4c71"
down_revision = "08b944954eba"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_MANDATORY_BOOKING_CONTACT",
        isActive=True,
        description="Rend obligatoire offer.bookingContact pour les offres retirables",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
