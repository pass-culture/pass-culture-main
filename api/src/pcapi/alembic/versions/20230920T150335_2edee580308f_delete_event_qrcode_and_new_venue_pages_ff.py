"""
Delete Event QR Code & New Venue Pages FF
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2edee580308f"
down_revision = "eade6ec3120d"
branch_labels = None
depends_on = None


def get_flag_venue():  # type: ignore [no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NEW_VENUE_PAGES",
        isActive=False,
        description="Utiliser la nouvelle version des pages d'edition et de creation de lieux",
    )


def get_flag_qr():  # type: ignore [no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="PRO_DISABLE_EVENTS_QRCODE",
        isActive=True,
        description="Active la possibilité de différencier le type d’envoi des billets \
            sur une offre et le retrait du QR code sur la réservation",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag_qr())
    feature.remove_feature_from_database(get_flag_venue())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag_qr())
    feature.add_feature_to_database(get_flag_venue())
