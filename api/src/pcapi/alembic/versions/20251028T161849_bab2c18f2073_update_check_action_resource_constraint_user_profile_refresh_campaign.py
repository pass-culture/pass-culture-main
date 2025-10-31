"""update check_action_resource_constraint to add userProfileRefreshCampaign field"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bab2c18f2073"
down_revision = "ab86e0dd784c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE action_history DROP CONSTRAINT IF EXISTS "check_action_resource" """)
    op.execute(
        """
ALTER TABLE action_history ADD CONSTRAINT "check_action_resource" CHECK
(
    (
        (num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId", "chronicleId", "userProfileRefreshCampaignId") >= 1)
        OR ("actionType" = 'BLACKLIST_DOMAIN_NAME'::text)
        OR ("actionType" = 'REMOVE_BLACKLISTED_DOMAIN_NAME'::text)
        OR ("actionType" = 'ROLE_PERMISSIONS_CHANGED'::text)
    )
) NOT VALID;
        """,
    )


def downgrade() -> None:
    op.execute("""ALTER TABLE action_history DROP CONSTRAINT IF EXISTS "check_action_resource" """)
    op.execute(
        """
ALTER TABLE action_history ADD CONSTRAINT "check_action_resource" CHECK
(
    (
        (num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId", "chronicleId") >= 1)
        OR ("actionType" = 'BLACKLIST_DOMAIN_NAME'::text)
        OR ("actionType" = 'REMOVE_BLACKLISTED_DOMAIN_NAME'::text)
        OR ("actionType" = 'ROLE_PERMISSIONS_CHANGED'::text)
    )
) NOT VALID;
        """,
    )
