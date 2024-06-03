"""Delete WIP_ENABLE_OFFER_PRICE_LIMITATION FF
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "34a1a2acff4f"
down_revision = "4c4e5383c6d3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_OFFER_PRICE_LIMITATION",
        isActive=True,
        description="Activer les règles de limitation de modification de prix des offres",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
