"""
Remove the feature flag WIP_ENABLE_OFFER_MARKDOWN_DESCRIPTION
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7ed9516f7af7"
down_revision = "943f189a4c71"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_OFFER_MARKDOWN_DESCRIPTION",
        isActive=True,
        description="Activer la description des offres collectives en markdown.",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
