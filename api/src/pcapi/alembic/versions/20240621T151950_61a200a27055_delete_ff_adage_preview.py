"""
Remove the feature flag WIP_ENABLE_ADAGE_PREVIEW_OFFER_IN_PRO
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "61a200a27055"
down_revision = "49b4f3ce3751"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_ADAGE_PREVIEW_OFFER_IN_PRO",
        isActive=True,
        description="Activer la prévisualisation d'une offre adage lors de la création/édition sur le portail pro",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
