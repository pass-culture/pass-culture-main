"""
Remore FF WIP_ENABLE_COOKIES_BANNER
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5ff88862400b"
down_revision = "59ecb650a586"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_COOKIES_BANNER",
        isActive=True,
        description="Active la nouvelle bannière de cookies",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
