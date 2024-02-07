"""
create debit note reference scheme
"""

from alembic import op


# pre/post deployment: pre
revision = "23e2d3b322ab"
down_revision = "4f6debc0238a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for year in (2024, 2025, 2026):
        op.execute(
            f"""
                INSERT INTO public.reference_scheme
                (name, prefix, year, "nextNumber", "numberPadding")
                VALUES ('debit_note.reference', 'A', {year}, 1, 7);
            """
        )


def downgrade() -> None:
    op.execute("DELETE FROM public.reference_scheme WHERE public.reference_scheme.name = 'debit_note.reference';")
