"""add educational institution program tables"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d5e7a47d4991"
down_revision = "7049d737cb3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "educational_institution_program",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "educational_institution_program_association",
        sa.Column("institutionId", sa.BigInteger(), nullable=False),
        sa.Column("programId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["institutionId"], ["educational_institution.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["programId"], ["educational_institution_program.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("institutionId", "programId"),
    )
    op.create_index(
        op.f("ix_educational_institution_program_association_institutionId"),
        "educational_institution_program_association",
        ["institutionId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_educational_institution_program_association_programId"),
        "educational_institution_program_association",
        ["programId"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO "educational_institution_program"(id, name, label, description)
        VALUES (1, 'marseille_en_grand', 'Marseille en grand', null)
    """
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_educational_institution_program_association_programId"),
        table_name="educational_institution_program_association",
    )
    op.drop_index(
        op.f("ix_educational_institution_program_association_institutionId"),
        table_name="educational_institution_program_association",
    )
    op.drop_table("educational_institution_program_association")
    op.drop_table("educational_institution_program")
