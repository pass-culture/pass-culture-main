"""add two new filters attribute for offer_validation_sub_rule"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b2947a6863b7"
down_revision = "250129872250"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE 'AUTHOR';")
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE 'EDITOR';")


def downgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute RENAME TO offer_validation_attribute_old")
    op.execute("""
        CREATE TYPE public.offer_validation_attribute AS ENUM (
            'CLASS_NAME',
            'NAME',
            'DESCRIPTION',
            'SIREN',
            'CATEGORY_ID',
            'SUBCATEGORY_ID',
            'WITHDRAWAL_DETAILS',
            'MAX_PRICE',
            'PRICE',
            'PRICE_DETAIL',
            'SHOW_SUB_TYPE',
            'ID',
            'TEXT',
            'FORMATS'
        );
    """)
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute("""
        ALTER TABLE offer_validation_sub_rule
            ALTER COLUMN attribute
            SET DATA TYPE offer_validation_attribute
            USING attribute::text::offer_validation_attribute;
    """)
    op.execute("DROP TYPE IF EXISTS offer_validation_attribute_old")
