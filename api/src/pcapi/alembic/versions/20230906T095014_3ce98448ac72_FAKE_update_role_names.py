""" FAKE : Update Role names with new names defined in Roles enum
Should have been a pre, not a post, but already merged, so we change it
"""


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3ce98448ac72"
down_revision = "9d1128058b6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
