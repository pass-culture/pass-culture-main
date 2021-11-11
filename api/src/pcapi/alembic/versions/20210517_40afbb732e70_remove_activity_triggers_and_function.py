"""Remove activity-related _triggers and function

Revision ID: 40afbb732e70
Revises: 97553c40978d
Create Date: 2021-05-17 19:07:35.396487

"""

import itertools

from alembic import op


# revision identifiers, used by Alembic.
revision = "40afbb732e70"
down_revision = "97553c40978d"
branch_labels = None
depends_on = None


TRIGGER_NAMES = ("audit_trigger_delete", "audit_trigger_insert", "audit_trigger_update")
TABLES = ("bank_information", "booking", "offer", "offerer", "stock", "user", "venue", "venue_provider")


def upgrade():
    for trigger, table in itertools.product(TRIGGER_NAMES, TABLES):
        op.execute(f'DROP TRIGGER "{trigger}" on "{table}"')
    op.execute("DROP FUNCTION create_activity")


def downgrade():
    pass  # to simplify things, there will be no going back
