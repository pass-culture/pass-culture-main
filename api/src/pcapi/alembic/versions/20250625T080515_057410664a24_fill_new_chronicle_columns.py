"""fill columns productIdentifierType, productIdentifier, clubType, identifierChoiceId for table chronicle"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "057410664a24"
down_revision = "4b97dba7262f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("UPDATE chronicle SET \"productIdentifierType\" = 'EAN'"))
    op.execute(sa.text('UPDATE chronicle SET "productIdentifier" = ean'))
    op.execute(sa.text("UPDATE chronicle SET \"clubType\" = 'BOOK'"))
    op.execute(sa.text('UPDATE chronicle SET "identifierChoiceId" = "eanChoiceId"'))


def downgrade() -> None:
    pass
