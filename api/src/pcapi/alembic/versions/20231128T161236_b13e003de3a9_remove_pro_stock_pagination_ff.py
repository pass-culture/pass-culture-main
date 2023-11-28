"""
Removes WIP_PRO_STOCK_PAGINATION Feature Flag
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f465cb05cc3e"
down_revision = "e7f8b2b66df7"
branch_labels = None
depends_on = None


def get_stock_pagination_flag():  # type: ignore [no-untyped-def]
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_PRO_STOCK_PAGINATION",
        isActive=False,
        description="Active la pagination pour les stocks",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_stock_pagination_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_stock_pagination_flag())
