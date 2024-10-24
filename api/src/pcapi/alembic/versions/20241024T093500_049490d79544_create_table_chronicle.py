"""create table chronicle"""

from alembic import op
import sqlalchemy as sa

from pcapi.utils.db import TSVector


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "049490d79544"
down_revision = "88c4d806c740"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_table(
        "chronicle",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("age", sa.SmallInteger(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("ean", sa.String(length=13), nullable=True),
        sa.Column("eanChoiceId", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("firstName", sa.String(length=128), nullable=True),
        sa.Column("formId", sa.String(length=20), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.Column("isIdentityDiffusible", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("isSocialMedia", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "__content_ts_vector__",
            TSVector(),
            sa.Computed("to_tsvector('french', content)", persisted=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chronicle_content___ts_vector__",
        "chronicle",
        ["__content_ts_vector__"],
        unique=False,
        postgresql_using="gin",
        concurently=True,
    )
    op.create_index(op.f("ix_chronicle_ean"), "chronicle", ["ean"], unique=False, concurently=True)


def downgrade() -> None:

    op.drop_index(
        op.f("ix_chronicle_ean"),
        table_name="chronicle",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_index(
        "ix_chronicle_content___ts_vector__",
        table_name="chronicle",
        postgresql_using="gin",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_table("chronicle")
