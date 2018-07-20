"""Add thingId XOR eventId on Recommendation

Revision ID: 11d603462200
Revises: 71be91495a74
Create Date: 2018-07-20 08:20:59.491980

"""
from alembic import op

# revision identifiers, used by Alembic.

revision = '11d603462200'
down_revision = '71be91495a74'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'check_reco_has_mediationid_xor_thingid_xor_eventid',
        'recommendation'
    )
    op.create_constraint(
        'check_reco_has_thingid_xor_eventid_xor_nothing',
        'recommendation'
    )


def downgrade():
    op.create_constraint(
        'check_reco_has_mediationid_xor_thingid_xor_eventid',
        'recommendation'
    )
    op.drop_constraint(
        'check_reco_has_thingid_xor_eventid_xor_nothing',
        'recommendation'
    )
