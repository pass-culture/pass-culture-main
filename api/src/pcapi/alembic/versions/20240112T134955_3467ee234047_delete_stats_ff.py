"""
Removes WIP_HOME_STATS and WIP_HOME_STATS_V2 Feature Flag
"""

# pre/post deployment: f0fbdcf9961d
# revision identifiers, used by Alembic.
revision = "3467ee234047"
down_revision = "f0fbdcf9961d"
branch_labels = None
depends_on = None


def get_stats_flag():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_HOME_STATS",
        isActive=False,
        description="Active la possibilité de voir les stats de consultation sur la page d'accueil",
    )


def get_stats_v2_flag():  # type: ignore[no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_HOME_STATS_V2",
        isActive=False,
        description="Active la V2 des stats de publication d'offres sur la page d'accueil",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_stats_v2_flag())
    feature.remove_feature_from_database(get_stats_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_stats_flag())
    feature.add_feature_to_database(get_stats_v2_flag())
