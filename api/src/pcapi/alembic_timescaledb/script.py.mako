"""${message}"""

from alembic import op
${imports if imports else ""}

# pre/post deployment: post (TimescaleDB-specific)
# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels: tuple[str] | None = ${repr(branch_labels)}
depends_on: list[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
