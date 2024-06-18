"""
Remove the feature flag WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f604375b4333"
down_revision = "0b8e5f65a615"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT",
        isActive=True,
        description="Activer le contact personnalisé pour les offres collectives",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
