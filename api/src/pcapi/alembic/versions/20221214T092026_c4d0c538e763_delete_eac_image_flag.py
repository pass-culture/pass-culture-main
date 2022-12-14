"""delete_eac_image_flag
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c4d0c538e763"
down_revision = "c59a8aa35f56"
branch_labels = None
depends_on = None


def get_flag():
    # Do not import `pcapi.models.feature` at module-level. It breaks
    # `alembic history` with a SQLAlchemy error that complains about
    # an unknown table name while initializing the ORM mapper.
    from pcapi.models import feature

    return feature.Feature(
        name="WIP_IMAGE_COLLECTIVE_OFFER",
        isActive=True,
        description="Active les images dans les offres collectives et les offres vitrines.",
    )


def upgrade() -> None:
    from pcapi.models import feature

    feature.remove_feature_from_database(get_flag())


def downgrade() -> None:
    from pcapi.models import feature

    feature.add_feature_to_database(get_flag())
