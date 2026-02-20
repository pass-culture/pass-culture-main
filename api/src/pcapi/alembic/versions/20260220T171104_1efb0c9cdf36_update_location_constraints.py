"""Update the location constraints
Remove temporary constraints used during the migration toward
the new architecture and add the new one.
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1efb0c9cdf36"
down_revision = "01d229a2edb1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_unique_offerer_address_per_label",
            "offerer_address",
            ["venueId", "type", "addressId", "label", "offererId"],
            unique=True,
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
        op.drop_index(
            op.f("ix_wip_unique_offerer_address_when_label_is_not_null"),
            table_name="offerer_address",
            postgresql_where="(label IS NOT NULL)",
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
        op.drop_index(
            op.f("ix_wip_unique_offerer_address_when_label_is_null"),
            table_name="offerer_address",
            postgresql_where='((label IS NULL) AND ("venueId" IS NOT NULL))',
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
        op.drop_index(
            op.f("ix_unique_offerer_address_per_label"),
            table_name="offerer_address",
            postgresql_where='((type IS NULL) AND ("venueId" IS NULL))',
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_unique_offerer_address_per_label"),
            "offerer_address",
            ["offererId", "addressId", "label"],
            unique=True,
            postgresql_where='((type IS NULL) AND ("venueId" IS NULL))',
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f("ix_wip_unique_offerer_address_when_label_is_null"),
            "offerer_address",
            ["offererId", "addressId", "type", "venueId"],
            unique=True,
            postgresql_where='((label IS NULL) AND ("venueId" IS NOT NULL))',
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f("ix_wip_unique_offerer_address_when_label_is_not_null"),
            "offerer_address",
            ["offererId", "addressId", "label", "type", "venueId"],
            unique=True,
            postgresql_where="(label IS NOT NULL)",
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
        op.drop_index(
            "ix_unique_offerer_address_per_label",
            table_name="offerer_address",
            postgresql_nulls_not_distinct=True,
            postgresql_concurrently=True,
        )
