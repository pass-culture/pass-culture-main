"""
remove WIP_ENABLE_NEW_NAV_AB_TEST
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4b41a69dfe71"
down_revision = "17aa8cf97ab4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_NAV_AB_TEST",
        isActive=True,
        description="Activer l'A/B test de la nouvelle navigation du portail pro.",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
