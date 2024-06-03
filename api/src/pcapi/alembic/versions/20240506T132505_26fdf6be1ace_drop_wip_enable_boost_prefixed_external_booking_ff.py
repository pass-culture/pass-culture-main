"""Drop wip_enable_boost_prefixed_external_booking FF
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "26fdf6be1ace"
down_revision = "571e971b5c73"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_BOOST_PREFIXED_EXTERNAL_BOOKING",
        isActive=True,
        description="Active les réservations externes boost avec préfixe",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
