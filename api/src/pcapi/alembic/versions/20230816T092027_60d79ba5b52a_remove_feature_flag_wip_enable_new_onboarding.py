"""Remove wip_enable_new_onboarding FF
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "60d79ba5b52a"
down_revision = "38d84c4d6248"
branch_labels = None
depends_on = None


def get_flag():  # type: ignore [no-untyped-def]
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_ENABLE_NEW_ONBOARDING",
        isActive=True,
        description="Active le nouvel onboarding sans SIREN",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
