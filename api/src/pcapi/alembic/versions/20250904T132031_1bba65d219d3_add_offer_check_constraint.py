"""FIXME: Cher·e auteur·ice de cette migration : le message ci-dessous
apparaît dans la sortie de `alembic history`. Tu dois supprimer ce
FIXME et faire en sorte que le message ci-dessous soit en anglais,
clair, en une seule ligne et lisible (un peu comme un message de
commit). Exemple : Add "blob" column to "offer" table.

add_offer_check_constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1bba65d219d3"
down_revision = "fe62e0063fc8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        ALTER TABLE offer
            ADD CONSTRAINT check_product_id_has_minimal_data
            CHECK (
                "productId" IS NULL
                OR (
                    description IS NULL
                    AND "durationMinutes" IS NULL
                    AND "jsonData" = '{}'
                )
            );
    """
    )


def downgrade() -> None:
    pass
