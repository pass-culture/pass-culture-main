"""Remove WIP_RECURRENCE feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5b80257fdb94"
down_revision = "33e76b6e3a77"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_RECURRENCE",
        isActive=True,
        description="Active l'ajout de dates récurrentes pour événements sur les offres individuelles",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
