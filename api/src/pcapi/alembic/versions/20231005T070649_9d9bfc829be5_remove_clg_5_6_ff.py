"""remove WIP_ADD_CLG_6_5_COLLECTIVE_OFFER ff"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9d9bfc829be5"
down_revision = "06ebfa9392fa"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ADD_CLG_6_5_COLLECTIVE_OFFER",
        isActive=True,
        description="Ouverture des offres collectives au 6ème et 5ème",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
