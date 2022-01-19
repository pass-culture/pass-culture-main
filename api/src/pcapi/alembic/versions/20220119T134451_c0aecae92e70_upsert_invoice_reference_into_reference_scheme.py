"""Upsert invoice.reference into reference_scheme
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c0aecae92e70"
down_revision = "6940a75b4417"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO reference_scheme ("name", "prefix", "year", "nextNumber", "numberPadding")
        VALUES
         ('invoice.reference', 'F', 2022, 1, 7),
         ('invoice.reference', 'F', 2023, 1, 7),
         ('invoice.reference', 'F', 2024, 1, 7),
         ('invoice.reference', 'F', 2025, 1, 7),
         ('invoice.reference', 'F', 2026, 1, 7)
         ON CONFLICT DO NOTHING;
        """
    )


def downgrade():
    pass
