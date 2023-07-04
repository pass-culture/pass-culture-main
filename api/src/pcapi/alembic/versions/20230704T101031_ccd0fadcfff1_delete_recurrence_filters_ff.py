"""
delete_recurrence_filters_ff
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ccd0fadcfff1"
down_revision = "c55b7be22565"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_RECURRENCE_FILTERS",
        isActive=True,
        description="Ajoute les filtres et le tri sur la vue liste des récurrences",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
