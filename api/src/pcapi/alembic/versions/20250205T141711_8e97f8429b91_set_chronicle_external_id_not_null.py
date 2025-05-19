"""set chronicle.externalId to not null"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8e97f8429b91"
down_revision = "7d06482102c6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('UPDATE chronicle SET "externalId"="formId" WHERE "externalId" is NULL;')
    op.alter_column("chronicle", "externalId", existing_type=sa.TEXT(), nullable=False)
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint("ix_chronicle_externalId", "chronicle", ["externalId"])


def downgrade() -> None:
    op.drop_constraint("ix_chronicle_externalId", "chronicle", type_="unique")
    op.alter_column("chronicle", "externalId", existing_type=sa.TEXT(), nullable=True)
