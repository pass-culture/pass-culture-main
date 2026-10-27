"""FIXME: Cher·e auteur·ice de cette migration : le message ci-dessous
apparaît dans la sortie de `alembic history`. Tu dois supprimer ce
FIXME et faire en sorte que le message ci-dessous soit en anglais,
clair, en une seule ligne et lisible (un peu comme un message de
commit). Exemple : Add "blob" column to "offer" table.

delete_offererId_from_offereraddress"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "677f894d6dc9"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # op.execute("UPDATE offerer_address SET offererId = NULL")

    # op.execute("ALTER TABLE offerer_address DROP CONSTRAINT IF EXISTS offerer_address_offererId_fkey")
    # op.execute("ALTER TABLE offerer_address ALTER COLUMN offererId SET NULL")

    op.drop_column("offerer_address", "offererId")


def downgrade() -> None:

    # op.execute("ALTER TABLE offerer_address DROP CONSTRAINT IF EXISTS offerer_address_offererId_fkey")

    op.add_column("offerer_address", sa.Column("offererId", sa.BIGINT(), autoincrement=False, nullable=False))
