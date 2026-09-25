"""FIXME: Cher·e auteur·ice de cette migration : le message ci-dessous
apparaît dans la sortie de `alembic history`. Tu dois supprimer ce
FIXME et faire en sorte que le message ci-dessous soit en anglais,
clair, en une seule ligne et lisible (un peu comme un message de
commit). Exemple : Add "blob" column to "offer" table.

add_extra_data_on_sso_table"""

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
