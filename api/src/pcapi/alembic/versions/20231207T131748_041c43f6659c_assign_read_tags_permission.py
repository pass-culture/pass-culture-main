"""Assign new READ_TAGS permission to backoffice roles which already manage tags
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "041c43f6659c"
down_revision = "1ce7e6391919"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT "roleId", (SELECT id FROM permission p WHERE p.name = 'READ_TAGS')
        FROM role_permission
        JOIN permission on role_permission."permissionId" = permission.id
        WHERE permission.name IN ('MANAGE_OFFERER_TAG', 'MANAGE_OFFERS_AND_VENUES_TAGS', 'MANAGE_TAGS_N2')
    """
    )


def downgrade() -> None:
    pass
