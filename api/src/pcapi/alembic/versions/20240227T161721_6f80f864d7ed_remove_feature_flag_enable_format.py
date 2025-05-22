"""
remove_feature_flag_enable_format
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6f80f864d7ed"
down_revision = "48b6b7074b64"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_FORMAT",
        isActive=True,
        description="Activer le remplacement des catégories/sous-catégories par les formats",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
