CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_address_geo_gist" ON "address" USING spgist (
    (
        ST_MakePoint(
            longitude :: double precision,
            latitude :: double precision
        ) :: geography
    )
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_stock_bookability" ON "stock" USING btree (
    "offerId",
    "beginningDatetime",
    "isSoftDeleted",
    "bookingLimitDatetime",
    "quantity",
    "dnBookedQuantity"
);