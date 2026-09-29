"""Add extra data in SSO table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7b723528671a"
down_revision = "48232008761a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("single_sign_on", sa.Column("ssoExtraData", JSONB, nullable=True, default=None))


def downgrade() -> None:
    op.drop_column("single_sign_on", "ssoExtraData")
