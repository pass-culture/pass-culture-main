"""remove_wip_improve_collective_status_ff
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "329eb64be6c5"
down_revision = "e7443f71e558"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_IMPROVE_COLLECTIVE_STATUS",
        isActive=True,
        description="Améliorer le suivi des status des offres et réservations collectives",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
