"""update action_history table's constraint
"""
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ce6fe5bab319"
down_revision = "9793c2c38cb5"
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
            )
            NOT VALID,

        DROP CONSTRAINT IF EXISTS
            "check_at_least_one_resource" ;

        COMMIT;
        """
    )

    op.execute("""SET SESSION statement_timeout = '900s'""")
    op.execute(
        """
        ALTER TABLE
            action_history
        VALIDATE CONSTRAINT
            check_at_least_one_resource_or_is_fraud_action
        """
    )

    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE
            action_history

        -- ensure constraint does not already exists
        DROP CONSTRAINT IF EXISTS
            "check_at_least_one_resource",

        -- this time NOT VALID cannot be followed by a VALIDATE
        -- CONSTRAINT since older rows could invalid.
        ADD CONSTRAINT
            "check_at_least_one_resource"
            CHECK ((num_nonnulls("userId", "offererId", "venueId") >= 1))
            NOT VALID,

        DROP CONSTRAINT IF EXISTS
            "check_at_least_one_resource_or_is_fraud_action" ;

        COMMIT
        """
    )

    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")
