"""remove WIP_ENABLE_COLLECTIVE_REQUEST feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e447c5675466"
down_revision = "d97c79fdee03"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_COLLECTIVE_REQUEST",
        isActive=True,
        description="Active la demande de création d'offre collective de la part des utilisateurs adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
