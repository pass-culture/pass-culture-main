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
revision = "3b9771e17f50"
down_revision = "6993fbbec133"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("single_sign_on", sa.Column("ssoExtraData", JSONB, nullable=True, default=None))


def downgrade() -> None:
    op.drop_column("single_sign_on", "ssoExtraData")
