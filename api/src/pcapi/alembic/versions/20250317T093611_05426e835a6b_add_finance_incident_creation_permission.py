"""Assign new CREATE_INCIDENTS permission to backoffice roles"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "05426e835a6b"
down_revision = "664bb71b3de0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO permission ("name", "category")
        VALUES ('CREATE_INCIDENTS', NULL)
        ON CONFLICT ("name") DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT DISTINCT id, (SELECT id FROM permission p WHERE p.name = 'CREATE_INCIDENTS')
        FROM public."role"
        WHERE role.name in ('support_n2', 'support_pro', 'support_pro_n2', 'fraude_conformite', 'daf')
        ON CONFLICT ("roleId", "permissionId") DO NOTHING
        """
    )


def downgrade() -> None:
    pass
