"""Remove WIP_BEHIND_L7_LOAD_BALANCER feature flag"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c8e741468d2a"
down_revision = "975f6274e3ce"
branch_labels = None
depends_on = None


def get_flag():
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_BEHIND_L7_LOAD_BALANCER",
        isActive=True,
        description="À activer/désactiver en même temps que le load balancer L7",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
