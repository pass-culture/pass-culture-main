"""remove WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "361fc0a4ba9b"
down_revision = "372a9e3069be"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def get_flag():  # type: ignore[no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS",
        isActive=False,
        description="Synchroniser les offres et stocks de cinéma avec les produits allociné",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
