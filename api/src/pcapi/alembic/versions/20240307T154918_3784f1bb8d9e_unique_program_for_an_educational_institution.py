"""Unique program for an educational institution"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3784f1bb8d9e"
down_revision = "23fa7b1b692e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_educational_institution_program_association_institutionId",
            table_name="educational_institution_program_association",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f("ix_educational_institution_program_association_institutionId"),
            "educational_institution_program_association",
            ["institutionId"],
            unique=True,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_educational_institution_program_association_institutionId"),
            table_name="educational_institution_program_association",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_educational_institution_program_association_institutionId",
            "educational_institution_program_association",
            ["institutionId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
