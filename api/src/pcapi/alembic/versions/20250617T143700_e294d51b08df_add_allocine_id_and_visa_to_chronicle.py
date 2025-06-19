"""create columns productIdentifierType, productIdentifier, clubType, identifierChoiceId for table chronicle"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.chronicles.models import ChronicleClubType
from pcapi.core.chronicles.models import ChronicleProductIdentifierType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e294d51b08df"
down_revision = "7cbc7b9e7230"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "chronicle", sa.Column("productIdentifierType", MagicEnum(ChronicleProductIdentifierType), nullable=True)
    )
    op.add_column("chronicle", sa.Column("productIdentifier", sa.Text(), nullable=True))
    op.add_column("chronicle", sa.Column("clubType", MagicEnum(ChronicleClubType), nullable=True))
    op.add_column("chronicle", sa.Column("identifierChoiceId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("chronicle", "productIdentifierType")
    op.drop_column("chronicle", "productIdentifier")
    op.drop_column("chronicle", "clubType")
    op.drop_column("chronicle", "identifierChoiceId")
