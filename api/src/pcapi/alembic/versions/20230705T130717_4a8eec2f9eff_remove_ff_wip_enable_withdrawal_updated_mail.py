"""
remove_ff_WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4a8eec2f9eff"
down_revision = "97cccec19d0e"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL",
        isActive=True,
        description="Envoie un mail aux jeunes qui ont réservé lorsque les modalités de retrait d'une offre sont changées",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
