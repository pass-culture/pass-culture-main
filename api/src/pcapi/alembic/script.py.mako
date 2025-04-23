"""FIXME: Cher·e auteur·ice de cette migration : le message ci-dessous
apparaît dans la sortie de `alembic history`. Tu dois supprimer ce
FIXME et faire en sorte que le message ci-dessous soit en anglais,
clair, en une seule ligne et lisible (un peu comme un message de
commit). Exemple : Add "blob" column to "offer" table.

${message}"""

from alembic import op

import sqlalchemy as sa
${imports if imports else ""}

# pre/post deployment: ${config.cmd_opts.head.split("@")[0]}
# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels: tuple[str] | None = ${repr(branch_labels)}
depends_on: list[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
