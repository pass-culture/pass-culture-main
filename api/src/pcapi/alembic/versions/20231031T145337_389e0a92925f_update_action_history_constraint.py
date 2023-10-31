"""Update constraint in action_history table
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "389e0a92925f"
down_revision = "2a720f939c92"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\'',
    )


def downgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\'',
    )
