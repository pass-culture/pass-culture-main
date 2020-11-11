"""add_new_ribs_upload_feature_flipping

Revision ID: 040875ff5d5b
Revises: 2b6541bb0076
Create Date: 2020-04-09 13:17:59.708958

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "040875ff5d5b"
down_revision = "8060a51c72f3"
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    NEW_RIBS_UPLOAD = "Permettre aux utilisateurs d" "uploader leur ribs via la nouvelle démarche DMS"


def upgrade():
    new_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
    )
    previous_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
    )

    previous_enum = sa.Enum(*previous_values, name="featuretoggle")
    new_enum = sa.Enum(*new_values, name="featuretoggle")
    temporary_enum = sa.Enum(*new_values, name="tmp_featuretoggle")

    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle" " USING name::text::tmp_featuretoggle")
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle" " USING name::text::featuretoggle")
    op.execute(
        """
            INSERT INTO feature (name, description, "isActive")
            VALUES ('%s', '%s', FALSE);
            """
        % (FeatureToggle.NEW_RIBS_UPLOAD.name, FeatureToggle.NEW_RIBS_UPLOAD.value)
    )
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    new_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
    )
    previous_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
    )

    previous_enum = sa.Enum(*previous_values, name="featuretoggle")
    new_enum = sa.Enum(*new_values, name="featuretoggle")
    temporary_enum = sa.Enum(*new_values, name="tmp_featuretoggle")

    op.execute("DELETE FROM feature WHERE name = 'NEW_RIBS_UPLOAD'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle" " USING name::text::tmp_featuretoggle")
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle" " USING name::text::featuretoggle")
    temporary_enum.drop(op.get_bind(), checkfirst=False)
