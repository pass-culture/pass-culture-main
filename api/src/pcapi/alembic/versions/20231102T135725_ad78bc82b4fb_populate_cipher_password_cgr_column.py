"""
Populate CGR `encryptedPassword` column
"""

from alembic import op

from pcapi.utils.crypto import encrypt


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad78bc82b4fb"
down_revision = "55e87bc5d320"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute("select * from cgr_cinema_details")

    for row in rows:
        op.execute(
            f"""update cgr_cinema_details set "encryptedPassword" = '{encrypt(row.password)}' where id = {row.id}"""
        )


def downgrade() -> None:
    op.execute("""update cgr_cinema_details set "encryptedPassword"=NULL""")
