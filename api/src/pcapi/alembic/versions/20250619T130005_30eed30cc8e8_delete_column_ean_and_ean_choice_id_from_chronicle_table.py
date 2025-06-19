"""delete columns ean and eanChoiceId from chronicle"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "30eed30cc8e8"
down_revision = "7fc9c1ffb338"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("chronicle", "ean")
    op.drop_column("chronicle", "eanChoiceId")


def downgrade() -> None:
    op.add_column("chronicle", sa.Column("ean", sa.Text(), nullable=True))
    op.execute(sa.text('UPDATE chronicle SET ean = "productIdentifier"'))
    op.add_column("chronicle", sa.Column("eanChoiceId", sa.Text(), nullable=True))
    op.execute(sa.text('UPDATE chronicle SET "eanChoiceId" = "identifierChoiceId"'))
