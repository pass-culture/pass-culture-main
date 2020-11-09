"""Add indexes for to be ISO production

Revision ID: e387ee2c380d
Revises: 6213b64185a5
Create Date: 2019-10-29 14:29:55.013272

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e387ee2c380d'
down_revision = '6213b64185a5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        CREATE INDEX IF NOT EXISTS "idx_api_key_offererId" ON api_key ("offererId");
        CREATE INDEX IF NOT EXISTS "idx_api_key_value" ON api_key ("value");

        CREATE INDEX IF NOT EXISTS "idx_bank_information_offererId" ON bank_information ("offererId");
        CREATE INDEX IF NOT EXISTS "idx_bank_information_venueId" ON bank_information ("venueId");

        CREATE INDEX IF NOT EXISTS "idx_favorite_mediationId" ON favorite ("mediationId");
        CREATE INDEX IF NOT EXISTS "idx_favorite_offerId" ON favorite ("offerId");
        CREATE INDEX IF NOT EXISTS "idx_favorite_userId" ON favorite ("userId");
        ALTER TABLE ONLY favorite ADD CONSTRAINT "favorite_mediationId_fkey" FOREIGN KEY ("mediationId") REFERENCES mediation(id);
        ALTER TABLE ONLY favorite ADD CONSTRAINT "favorite_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES offer(id);
        ALTER TABLE ONLY favorite ADD CONSTRAINT "favorite_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"(id);

        CREATE INDEX IF NOT EXISTS "idx_offer_criterion_criterionId" ON offer_criterion ("criterionId");
        CREATE INDEX IF NOT EXISTS "idx_offer_criterion_offerId" ON offer_criterion ("offerId");
        ALTER TABLE ONLY offer_criterion ADD CONSTRAINT "offer_criterion_criterionId_fkey" FOREIGN KEY ("criterionId") REFERENCES criterion(id);
        ALTER TABLE ONLY offer_criterion ADD CONSTRAINT "offer_criterion_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES offer(id);
        '''
    )


def downgrade():
    op.execute(
        '''
        DROP INDEX IF EXISTS "idx_api_key_offererId";
        DROP INDEX IF EXISTS "idx_api_key_value";

        DROP INDEX IF EXISTS "idx_bank_information_offererId";
        DROP INDEX IF EXISTS "idx_bank_information_venueId";

        DROP INDEX IF EXISTS "idx_favorite_mediationId";
        DROP INDEX IF EXISTS "idx_favorite_offerId";
        DROP INDEX IF EXISTS "idx_favorite_userId";

        DROP INDEX IF EXISTS "idx_offer_criterion_criterionId";
        DROP INDEX IF EXISTS "idx_offer_criterion_offerId";
        '''
    )
