"""Remove WIP_REQUIRE_PRICE_IN_STOCK_API feature flag."""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "06854dddfe34"
down_revision = "d78898f839df"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_REQUIRE_PRICE_IN_STOCK_API",
        isActive=True,
        description="Requiert le champ de prix dans l'API Stock",
    )


def upgrade():
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade():
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
