"""Add ENABLE_ID_CHECK_RETENTION feature flag

Revision ID: e85a73abc5a7
Revises: a3a703bc054b
Create Date: 2021-06-04 08:00:13.749757

ENABLE_ID_CHECK_RETENTION was deleted in the following commit:
commit bae303a949 (PC-15780)[API] refactor: remove Feature Flip ENABLE_ID_CHECK_RETENTION

"""


# revision identifiers, used by Alembic.
revision = "e85a73abc5a7"
down_revision = "a3a703bc054b"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
