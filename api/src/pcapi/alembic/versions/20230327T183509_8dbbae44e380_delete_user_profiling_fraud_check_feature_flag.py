"""Delete USER_PROFILING_FRAUD_CHECK feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8dbbae44e380"
down_revision = "56bba24a7f57"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="USER_PROFILING_FRAUD_CHECK",
        isActive=False,
        description="Détection de la fraude basée sur le profil de l''utilisateur",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
