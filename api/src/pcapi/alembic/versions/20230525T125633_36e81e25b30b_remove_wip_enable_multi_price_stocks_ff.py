"""remove WIP_ENABLE_MULTI_PRICE_STOCKS feature flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "36e81e25b30b"
down_revision = "5b80257fdb94"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_MULTI_PRICE_STOCKS",
        isActive=True,
        description="Active la fonctionnalité multi-tarif pour les offres individuelles",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
