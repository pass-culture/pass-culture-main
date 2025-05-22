"""delete WIP_ENABLE_BOOST_TWO_STAGES_BOOKING FF"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5316ce0cc1dd"
down_revision = "c551c042d2e6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_BOOST_TWO_STAGES_BOOKING",
        isActive=True,
        description="Activer la réservation Boost en 2 étapes.",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
