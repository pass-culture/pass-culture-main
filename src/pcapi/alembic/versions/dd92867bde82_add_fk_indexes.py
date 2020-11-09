"""Add index on FKs

Revision ID: dd92867bde82
Revises: 3f915af15e86
Create Date: 2019-02-12 09:26:59.507592

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'dd92867bde82'
down_revision = '3f915af15e86'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
          CREATE INDEX IF NOT EXISTS "ix_activity_transactionId" ON activity USING btree ("transaction_id");
          CREATE INDEX IF NOT EXISTS "ix_offer_eventId" ON offer USING btree ("eventId");
          CREATE INDEX IF NOT EXISTS "ix_offer_thingId" ON offer USING btree ("thingId");
          CREATE INDEX IF NOT EXISTS "ix_payment_statuspaymentId" ON payment_status USING btree ("paymentId");
          CREATE INDEX IF NOT EXISTS "ix_payment_transactionId" ON payment USING btree ("transactionId");
          CREATE INDEX IF NOT EXISTS "ix_booking_recommendationId" ON booking USING btree ("recommendationId");
          CREATE INDEX IF NOT EXISTS "ix_user_offerer_offererId" ON user_offerer USING btree ("offererId");
          CREATE INDEX IF NOT EXISTS "ix_recommendationinviteforEventOccurrenceId" ON recommendation USING btree ("inviteforEventOccurrenceId");
        """)
    pass


def downgrade():
    op.execute(
        """
          DROP INDEX "ix_activity_transactionId";
          DROP INDEX "ix_offer_eventId";
          DROP INDEX "ix_offer_thingId";
          DROP INDEX "ix_payment_statuspaymentId";
          DROP INDEX "ix_payment_transactionId";
          DROP INDEX "ix_booking_recommendationId";
          DROP INDEX "ix_user_offerer_offererId";
          DROP INDEX "ix_recommendationinviteforEventOccurrenceId";
        """)
    pass
