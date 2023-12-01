"""
Remove FF WIP_OFFER_TO_INSTITUTION
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b6a4121a0971"
down_revision = "f465cb05cc3e"
branch_labels = None
depends_on = None


def get_flag():  # type:ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_OFFER_TO_INSTITUTION",
        isActive=True,
        description="Activer le fléchage d'une offre à un établissement",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
