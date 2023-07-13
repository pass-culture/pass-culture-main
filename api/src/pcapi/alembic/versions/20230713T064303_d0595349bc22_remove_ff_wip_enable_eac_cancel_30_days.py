"""
remove_ff_wip_enable_eac_cancel_30_days
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d0595349bc22"
down_revision = "097c6d306952"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_EAC_CANCEL_30_DAYS",
        isActive=True,
        description="EAC délai annulation 30 Jours par defaut au lieu de 15",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
