---
title: Pass Culture API change logs
---

# Change logs

:::warning
💡 Important notice some old resources are going to be removed in the coming months.

- If you were using `/v1/stock` to manage stocks, you will have to migrate to this endpoint : [/public/v1/product/ean](/rest-api#tag/Product-offer-bulk-operations/operation/PostProductOfferByEan). The endpoint `/v1/stock` will not be available anymore starting from Septembre, the 31st 2024.
- If you were using `/v1/bookings` to manage bookings, you will have to migrate to those endpoints [/public/v1/bookings](/rest-api#tag/Bookings).  The endpoint `/v1/bookings` will not be available anymore starting from March, the 31st 2025.
:::

## June 2023

- You can now specify your own id when you [create an individual event offer](/rest-api#tag/Event-offers/operation/PostEventOffer) and/or [create stock for this event](/rest-api#tag/Event-offer-stocks/operation/PostEventStocks). This id is called `idAtProvider` and will be send to your ticketing system when a beneficiary books a ticket.

## March 2023

- Collective categories have been replaced by educational format to be more accurate. Collective categories will be definitively removed on September, the 31st 2024.

## February 2023

- New music types have been defined for musical events, CD and vinyls. We adopted Titelive classification. Older types will be definitively removed on September, the 31st 2024.

## January 2023

- Rate limiting has been implemented to the Pass Culture public API. **You are now limited to 200 requests/minute** per API key.
  Once this limit reached, you will received a `429 Too Many Requests` error message. You will then need to back down.
