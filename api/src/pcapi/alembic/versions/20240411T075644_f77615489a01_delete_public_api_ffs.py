"""Delete unused FFs for public Apis."""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f77615489a01"
down_revision = "01b735d5e27f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_features():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return [
        feature.Feature(
            name="ENABLE_CHARLIE_BOOKINGS_API", isActive=True, description="Active la réservation via l'API Charlie"
        ),
        feature.Feature(
            name="WIP_ENABLE_OFFER_CREATION_API_V1",
            isActive=True,
            description="Active la création d'offres via l'API v1",
        ),
        feature.Feature(
            name="WIP_ENABLE_EVENTS_WITH_TICKETS_FOR_PUBLIC_API",
            isActive=True,
            description="Activer la création d'évènements avec tickets dans l'API publique",
        ),
    ]


def upgrade() -> None:
    from pcapi.models import feature

    for feature_flag in get_features():
        feature.remove_feature_from_database(feature_flag)


def downgrade() -> None:
    from pcapi.models import feature

    for feature_flag in get_features():
        feature.add_feature_to_database(feature_flag)
