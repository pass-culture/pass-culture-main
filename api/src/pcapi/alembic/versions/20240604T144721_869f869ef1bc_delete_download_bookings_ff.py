"""
Removes WIP_HOME_STATS and WIP_HOME_STATS_V2 Feature Flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "869f869ef1bc"
down_revision = "1161bdcd0100"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_DOWNLOAD_BOOKINGS",
        isActive=True,
        description="Activer le téléchargement des réservations",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
