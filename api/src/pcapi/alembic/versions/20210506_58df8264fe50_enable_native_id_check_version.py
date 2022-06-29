"""Enable native id check version

Revision ID: 58df8264fe50
Revises: c2e2425fbac6
Create Date: 2021-05-06 15:14:21.619714

This migration previously added the FF ENABLE_NATIVE_ID_CHECK_VERSION that was later deleted as it's obsolete

"""


# revision identifiers, used by Alembic.
revision = "58df8264fe50"
down_revision = "c2e2425fbac6"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
