"""
remove_feature_flag_new_adage_offer_design
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = 'e4cd12df4552'
down_revision = '06ecb5800626'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_ADAGE_OFFER_DESIGN",
        isActive=True,
        description="Activer le nouveau design des offres sur adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
