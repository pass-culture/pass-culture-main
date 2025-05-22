"""Remove `WIP_ENABLE_RATE_LIMITING` feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "48b6b7074b64"
down_revision = "1e3979b7adb0"
branch_labels = None
depends_on = None


def get_flag():
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_RATE_LIMITING",
        isActive=False,
        description="Active le rate limiting",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
