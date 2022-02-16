"""set JSONB fields as used ones
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e9ddaad94156"
down_revision = "932e613984b3"
branch_labels = None
depends_on = None


# Those fields can be altered because:
# - it belongs to the `offer_validation_config` table that contain very few records
# - a test on staging shows that it is very quick for the table `email`
fields_to_be_renamed = [
    ("email", "content"),
    ("offer_validation_config", "specs"),
]


def rename(table: str, field: str) -> None:
    op.execute(f'ALTER TABLE {table} RENAME COLUMN "{field}" TO "{field}Old";')
    op.execute(f'ALTER TABLE {table} ALTER COLUMN "{field}Old" DROP NOT NULL;')
    op.execute(f'ALTER TABLE {table} RENAME COLUMN "{field}New" TO "{field}";')
    op.execute(f'ALTER TABLE {table} ALTER COLUMN "{field}" SET NOT NULL;')


def unrename(table: str, field: str) -> None:
    op.execute(f'ALTER TABLE {table} ALTER COLUMN "{field}" DROP NOT NULL;')
    op.execute(f'ALTER TABLE {table} RENAME COLUMN "{field}" TO "{field}New";')
    op.execute(f'ALTER TABLE {table} ALTER COLUMN "{field}Old" SET NOT NULL;')
    op.execute(f'ALTER TABLE {table} RENAME COLUMN "{field}Old" TO "{field}";')


def upgrade():
    for table, field in fields_to_be_renamed:
        rename(table, field)


def downgrade():
    for table, field in fields_to_be_renamed:
        unrename(table, field)
