---
title: Pass Culture API change logs
---

# Change logs

:::warning
💡 Important notice some old resources are going to be removed in the coming months.

- If you were using `/v2/venue/<venue_id>/stocks` to manage stocks, you will have to migrate to this endpoint : [/public/offers/v1/products/ean](/rest-api#tag/Product-offer-bulk-operations/operation/PostProductOfferByEan). The endpoint `/v2/stock` will not be available anymore starting from September, the 31st 2024.
- If you were using `/v2/bookings` to manage bookings, you will have to migrate to those endpoints [/public/bookings/v1/bookings](/rest-api#tag/Bookings).  The endpoint `/v2/bookings` will not be available anymore starting from March, the 31st 2025.

**You can find a migration tutorial [here](/docs/tutorials/migrate-to-the-new-api).**
:::

## October 2024

- The [**"Get event stocks" endpoint**](/rest-api#tag/Event-offer-stocks/operation/GetEventStocks) now supports filtering results by the `idsAtProvider` parameter (ie. by your own ids)

## September 2024

### `idAtProvider` in price category
- You can now specify your own id when you [**create price categories**](/rest-api#tag/Event-offer-prices/operation/PostEventPriceCategories), or when you [**update a price category**](/rest-api#tag/Event-offer-prices/operation/PatchEventPriceCategory), by adding an `idAtProvider` to your JSON payload.
- You can now access your event price categories using [**this endpoint**](/rest-api#tag/Event-offer-prices/operation/GetEventPriceCategories) and filter them using the `idsAtProvider` parameter
- Your price category id is now sent in [**our ticket request message**](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system#-our-request-payload) in the `price_category_id_at_provider` key

### EANs availability check
- You can now check if your EANs are available for bulk upsert using [**this endpoint**](/rest-api#tag/Product-offer-bulk-operations/operation/CheckEansAvailability)

## July 2024

- You can now access your provider information using [**this endpoint**](/rest-api#tag/Providers/operation/GetProvider).
- You can now set your messaging URLs using the API. Futhermore you can now specify them a 2 levels: either at [**provider level**](/rest-api#tag/Providers/operation/UpdateProvider) or at [**venue level**](/rest-api#tag/Providers/operation/UpdateVenueExternalUrls).
- `enableDoubleBookings` field's default value is now `true` on event creation or update.

## June 2024

- You can now specify your own id when you [**create an individual event offe**r](/rest-api#tag/Event-offers/operation/PostEventOffer) and/or [**create stock for this event**](/rest-api#tag/Event-offer-stocks/operation/PostEventStocks). This id is called `idAtProvider` and will be sent to your ticketing system when a beneficiary books a ticket ; in the message payload, it is called `offer_id_at_provider`.
- You can now specify you own id when you [**create stocks for an event offer**](/rest-api#tag/Event-offer-stocks/operation/PostEventStocks). This id called `idAtProvider` and will be sent to your ticketing system when a beneficiary books a ticket ; in the message payload, it is called `stock_id_at_provider`.

## March 2024

- Collective categories have been replaced by educational format to be more accurate. Collective categories will be definitively removed on September, the 31st 2024.

## February 2024

- New music types have been defined for musical events, CD and vinyls. We adopted Titelive classification. Older types will be definitively removed on September, the 31st 2024.

## January 2024

- Rate limiting has been implemented to the Pass Culture public API. **You are now limited to 200 requests/minute** per API key.
  Once this limit reached, you will received a `429 Too Many Requests` error message. You will then need to back down.
