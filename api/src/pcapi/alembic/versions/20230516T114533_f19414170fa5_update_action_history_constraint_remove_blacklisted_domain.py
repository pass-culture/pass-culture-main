"""update action_history constraint (remove blacklisted domain)
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f19414170fa5"
down_revision = "53c1de704b63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        BEGIN;
        ALTER TABLE
            action_history
        -- ensure constraint does not already exists
        DROP CONSTRAINT IF EXISTS
            "check_at_least_one_resource_or_is_fraud_action",
        -- update constraint
        -- use NOT VALID to avoid a lock. And since this new constraint
        -- is more flexible than the previous version, there is no need
        -- to run VALIDATE CONSTRAINT since older rows will also be
        -- valid with this update.
        ADD CONSTRAINT
            "check_at_least_one_resource_or_is_fraud_action"
            CHECK (
                num_nonnulls("userId", "offererId", "venueId") >= 1
                OR "actionType" = 'BLACKLIST_DOMAIN_NAME'
                OR "actionType" = 'REMOVE_BLACKLISTED_DOMAIN_NAME'
            )
            NOT VALID ;

        COMMIT;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        BEGIN;
        ALTER TABLE
            action_history
        -- ensure constraint does not already exists
        DROP CONSTRAINT IF EXISTS
            "check_at_least_one_resource_or_is_fraud_action",
        -- update constraint
        -- use NOT VALID to avoid a lock. And since this new constraint
        -- is more flexible than the previous version, there is no need
        -- to run VALIDATE CONSTRAINT since older rows will also be
        -- valid with this update.
        ADD CONSTRAINT
            "check_at_least_one_resource_or_is_fraud_action"
            CHECK (
                num_nonnulls("userId", "offererId", "venueId") >= 1
                OR "actionType" = 'BLACKLIST_DOMAIN_NAME'
            )
            NOT VALID;

        COMMIT;
        """
    )
