"""fill isEmailValidated

Revision ID: bc4ad3f45b5c
Revises: faa02accb1c4
Create Date: 2020-11-17 20:47:32.588635

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "bc4ad3f45b5c"
down_revision = "faa02accb1c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""UPDATE "user" SET "isEmailValidated"=false WHERE "password" IS NULL""")
    op.execute("""UPDATE "user" SET "isEmailValidated"=true WHERE "password" IS NOT NULL""")


def downgrade() -> None:
    pass
