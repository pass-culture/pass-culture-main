"""Remove legacy DISABLE_STORE_REVIEW feature flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c59a8aa35f56"
down_revision = "e7a7e2b3581d"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="DISABLE_STORE_REVIEW",
        isActive=False,
        description="Désactive la demande de notation sur les stores à la suite d’une réservation",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
