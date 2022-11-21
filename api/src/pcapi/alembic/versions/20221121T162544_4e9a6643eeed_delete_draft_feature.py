"""delete_draft_feature
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4e9a6643eeed"
down_revision = "d08bfa402042"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="OFFER_DRAFT_ENABLED",
        isActive=True,
        description="Active la fonctionnalités de création d'offre en brouillon",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
