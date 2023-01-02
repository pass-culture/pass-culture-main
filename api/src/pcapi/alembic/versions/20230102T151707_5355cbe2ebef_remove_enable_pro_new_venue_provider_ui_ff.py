"""remove_enable_pro_new_venue_provider_ui_ff
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5355cbe2ebef"
down_revision = "3b199dcfba04"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_PRO_NEW_VENUE_PROVIDER_UI",
        isActive=False,
        description="Activer le nouveau affichage de la section synchronisation sur la page lieu",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
