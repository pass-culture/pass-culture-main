"""
remove ENABLE_PRO_TITELIVE_MUSIC_GENRES
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ac46cd60fe3f"
down_revision = "9708ed7dcc65"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_PRO_TITELIVE_MUSIC_GENRES",
        isActive=True,
        description="Activer l'utilisation des genres musicaux Titelive pour les pros",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
