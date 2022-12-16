"""remove enable_new_identification_flow feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2a2df641b70d"
down_revision = "c4d0c538e763"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_NEW_IDENTIFICATION_FLOW",
        isActive=True,
        description="Activer le nouveau flux d'inscription jeune pré-Ubble",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
