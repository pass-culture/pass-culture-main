"""Remove FF ENABLE_CGR_TIMEOUT"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a613c5bc707a"
down_revision = "4df45e259f14"
branch_labels = None
depends_on = None


def get_flag():
    from pcapi.models import feature

    return feature.Feature(
        name="ENABLE_CGR_TIMEOUT",
        isActive=True,  # feature disable by default
        description="Active la prise en compte du timeout dans l'api CGR ",  #  <- adapter aussi
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
