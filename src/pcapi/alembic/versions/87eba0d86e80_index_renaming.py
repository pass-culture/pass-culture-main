"""Index renaming

Revision ID: 87eba0d86e80
Revises: 1d5f4822d8a2
Create Date: 2020-11-27 09:42:25.369573

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "87eba0d86e80"
down_revision = "1d5f4822d8a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    ALTER INDEX "idx_bank_information_offererId" RENAME TO "ix_bank_information_offererId";
    ALTER INDEX "idx_bank_information_venueId" RENAME TO "ix_bank_information_venueId";
    ALTER INDEX "idx_beneficiary_import_beneficiaryId" RENAME TO "ix_beneficiary_import_beneficiaryId";
    ALTER INDEX "idx_beneficiary_import_status_beneficiaryImportId" RENAME TO "ix_beneficiary_import_status_beneficiaryImportId";
    ALTER INDEX "idx_favorite_mediationId" RENAME TO "ix_favorite_mediationId";
    ALTER INDEX "idx_favorite_offerId" RENAME TO "ix_favorite_offerId";
    ALTER INDEX "idx_favorite_userId" RENAME TO "ix_favorite_userId";
    ALTER INDEX "feature_name_key" RENAME TO "ix_feature_name";
    ALTER INDEX "idx_offer_criterion_offerId" RENAME TO "ix_offer_criterion_offerId";
    ALTER INDEX "ix_payment_statuspaymentId" RENAME TO "ix_payment_status_paymentId";
    ALTER INDEX "idx_provider_name" RENAME TO "ix_provider_name";
    ALTER INDEX "idx_venue_provider_providerId" RENAME TO "ix_venue_provider_providerId";
    ALTER INDEX "ix_venue_provider_price_rule_venueProviderId" RENAME TO "ix_allocine_venue_provider_price_rule_allocineVenueProviderId";
    """
    )


def downgrade() -> None:
    op.execute(
        """
    ALTER INDEX "ix_bank_information_offererId" RENAME TO "idx_bank_information_offererId";
    ALTER INDEX "ix_bank_information_venueId" RENAME TO "idx_bank_information_venueId";
    ALTER INDEX "ix_beneficiary_import_beneficiaryId" RENAME TO "idx_beneficiary_import_beneficiaryId";
    ALTER INDEX "ix_beneficiary_import_status_beneficiaryImportId" RENAME TO "idx_beneficiary_import_status_beneficiaryImportId";
    ALTER INDEX "ix_favorite_mediationId" RENAME TO "idx_favorite_mediationId";
    ALTER INDEX "ix_favorite_offerId" RENAME TO "idx_favorite_offerId";
    ALTER INDEX "ix_favorite_userId" RENAME TO "idx_favorite_userId";
    ALTER INDEX "ix_feature_name" RENAME TO "feature_name_key";
    ALTER INDEX "ix_offer_criterion_offerId" RENAME TO "idx_offer_criterion_offerId";
    ALTER INDEX "ix_payment_status_paymentId" RENAME TO "ix_payment_statuspaymentId";
    ALTER INDEX "ix_provider_name" RENAME TO "idx_provider_name";
    ALTER INDEX "ix_venue_provider_providerId" RENAME TO "idx_venue_provider_providerId";
    ALTER INDEX "ix_allocine_venue_provider_price_rule_allocineVenueProviderId" RENAME TO "ix_venue_provider_price_rule_venueProviderId";
    """
    )
