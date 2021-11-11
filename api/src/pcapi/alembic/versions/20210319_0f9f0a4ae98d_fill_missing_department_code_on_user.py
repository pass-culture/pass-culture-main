"""fill_missing_department_code_on_user

Revision ID: 0f9f0a4ae98d
Revises: 2a602bd22f5d
Create Date: 2021-03-19 09:43:04.464965

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0f9f0a4ae98d"
down_revision = "2a602bd22f5d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        'UPDATE "user" SET "postalCode" = rpad("departementCode", 5, \'0\') WHERE "departementCode" IS '
        'NOT NULL AND "postalCode" IS NULL;'
    )


def downgrade() -> None:
    pass
