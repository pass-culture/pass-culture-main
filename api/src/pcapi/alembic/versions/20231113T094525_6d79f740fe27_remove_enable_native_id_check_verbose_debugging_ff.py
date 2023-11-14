"""Remove ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6d79f740fe27"
down_revision = "b80e58c59d0e"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING",
        isActive=False,
        description="Active le mode debug Firebase pour l'Id Check intégrée à l'application native",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
