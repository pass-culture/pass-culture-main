"""Delete feature flag WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c3eff57a0838"
down_revision = "7e51a47a52ef"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_EAC_ENABLE_NEW_AUTHENTICATION_PUBLIC_API",
        isActive=False,
        description="Active la gestion des providers dans l'api publique EAC",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
