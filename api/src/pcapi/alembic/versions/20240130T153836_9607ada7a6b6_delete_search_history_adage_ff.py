"""
Remove FF WIP_ENABLE_SEARCH_HISTORY_ADAGE
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9607ada7a6b6"
down_revision = "4f738fc2e54a"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_SEARCH_HISTORY_ADAGE",
        isActive=True,
        description="Activer la possibilité de voir l'historique des recherches sur adage",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
