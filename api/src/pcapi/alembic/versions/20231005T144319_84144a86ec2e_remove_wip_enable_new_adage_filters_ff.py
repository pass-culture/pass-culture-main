"""remove WIP_ENABLE_NEW_ADAGE_FILTERS ff"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "84144a86ec2e"
down_revision = "f72b113cfe59"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_ADAGE_FILTERS",
        isActive=True,
        description="Active les nouveaux filtres adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
