"""Set default value for address."isManualEdition" """

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "17aa8cf97ab4"
down_revision = "ce44550d83cb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(sa.text('UPDATE address SET "isManualEdition" = false WHERE "isManualEdition" is NULL;'))


def downgrade() -> None:
    pass
