"""Delete ENABLE_BACKOFFICE_API feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d3b0bc11c80a"
down_revision = "ba7ab326779e"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_BACKOFFICE_API",
        isActive=False,
        description="Autorise l'accès à l'API backoffice",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
