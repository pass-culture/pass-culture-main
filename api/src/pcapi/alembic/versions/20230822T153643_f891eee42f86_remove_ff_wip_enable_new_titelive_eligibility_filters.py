"""
Remove feature flip WIP_ENABLE_NEW_TITELIVE_ELIGIBILITY_FILTERS

remove_ff_wip_enable_new_titelive_eligibility_filters
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f891eee42f86"
down_revision = "620bcd1b6630"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_TITELIVE_ELIGIBILITY_FILTERS",
        isActive=True,
        description="Activer les nouveaux filtres d'éligibilité Tite Live",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
