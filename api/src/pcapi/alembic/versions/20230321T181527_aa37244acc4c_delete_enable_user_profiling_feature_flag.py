"""Delete ENABLE_USER_PROFILING feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "aa37244acc4c"
down_revision = "2598542274a5"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_USER_PROFILING",
        isActive=False,
        description="Active l'étape USER_PROFILING dans le parcours d'inscription des jeunes de 18 ans",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
