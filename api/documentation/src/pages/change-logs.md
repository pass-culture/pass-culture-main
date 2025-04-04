---
title: Pass Culture API change logs
---

# Change logs

:::warning
💡 Important notice some old resources are going to be removed in the coming months.

- If you were using `/v2/venue/<venue_id>/stocks` to manage stocks, you will have to migrate to this endpoint : [/public/offers/v1/products/ean](/rest-api#tag/Product-Offer-Bulk-Operations/operation/PostProductOfferByEan). The endpoint `/v2/stock` will not be available anymore starting from September, the 31st 2024.
- If you were using `/v2/bookings` to manage bookings, you will have to migrate to those endpoints [/public/bookings/v1/bookings](/rest-api#tag/Bookings).  The endpoint `/v2/bookings` will not be available anymore starting from June, the 30th 2025.

**You can find a migration tutorial [here](/docs/tutorials/migrate-to-the-new-api).**
:::

## February 2025

- You can specify a `publicationDate` precise to the quarter of hour using the [**Create Product Offer endpoint**](/rest-api#tag/Product-Offers/operation/PostProductOffer) and [**Create Event Offer endpoint**](/rest-api#tag/Event-Offers/operation/PostEventOffer).
- The `isActive` and `isSoldOut` fields have been deprecated in the [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic).
- The `isActive` attribute have been deprecated in the body and in return value of [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic), [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic).

## January 2025
- The `beginningDatetime` has been removed from the following endpoints:
  - Removed from the return value:
    - [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic)
    - [**Get Collective Offers endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOffersPublic)
  - Removed from the input body and the return value:
    - [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic)
    - [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic)
  Please use the `startDatetime` and `endDatetime` fields instead.
  The `startDatetime` field will be required when creating a collective offer and its value will be copied to `endDatetime` if `endDatetime` is not provided.

## December 2024

### Individual offers endpoints

- You can fetch a Venue by SIRET using the [**Get Venue endpoint**](/rest-api#tag/Venues/operation/GetVenueBySiret)
- You can now filter events ([**Get Event Offers endpoint**](/rest-api#tag/Event-Offers/operation/GetEvents)) and products ([**Get Product Offers endpoint**](/rest-api#tag/Product-Offers/operation/GetProducts)) using the `addressId` parameter.

### Collective offers endpoints

- The `subcategoryId` field has been removed from collective offers. The attribute is not returned anymore in the response of the [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic) and the [**Get Collective Offers endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOffersPublic)
- You must now only use the `formats` field (and not `subcategoryId`) to specify the educational format of your collective offer in the [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic) and the [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic). The `formats` field is required when creating a collective offer.


## November 2024

- You can edit the name of an event using the [**Update Event Offer endpoint**](/rest-api#tag/Event-Offers/operation/EditEvent)

## October 2024

### Addresses endpoints

:::info
New endpoints allow you to specify that your offer is available at a location different from your venue. Learn how to use them in [**our documentation**](/rest-api#tag/Addresses).
:::


- **Search Addresses:** You can now search for addresses in the pass Culture database using the [**Search Addresses endpoint**](/rest-api#tag/Addresses/operation/SearchAddresses)
- **Get Address:** You can now retrieve an existing address from the pass Culture database with the [**Get Address endpoint**](/rest-api#tag/Addresses/operation/GetAddress)
- **Create Address:** You can add an address to the pass Culture database with the [**Create Address endpoint**](/rest-api#tag/Addresses/operation/CreateAddress)

### Stocks endpoints
- The [**"Get event stocks" endpoint**](/rest-api#tag/Event-Offer-Stocks/operation/GetEventStocks) now supports filtering results by the `idsAtProvider` parameter (ie. by your own ids)

## September 2024

### `idAtProvider` in price category
- You can now specify your own id when you [**create price categories**](/rest-api#tag/Event-Offer-Price-Categories/operation/PostEventPriceCategories), or when you [**update a price category**](/rest-api#tag/Event-Offer-Price-Categories/operation/PatchEventPriceCategory), by adding an `idAtProvider` to your JSON payload.
- You can now access your event price categories using [**this endpoint**](/rest-api#tag/Event-Offer-Price-Categories/operation/GetEventPriceCategories) and filter them using the `idsAtProvider` parameter
- Your price category id is now sent in [**our ticket request message**](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system#-our-request-payload) in the `price_category_id_at_provider` key

### EANs availability check
- You can now check if your EANs are available for bulk upsert using [**this endpoint**](/rest-api#tag/Product-offer-bulk-operations/operation/CheckEansAvailability)

### Collective booking status (integration only) 
It is possible to change the status of collective booking into the **integration** environment. We have created new endpoints to modify these statuses and simulate the booking timeline on the Adage side. Please check [rest api documentation](/rest-api#tag/Adage-Mock-(Collective-Bookings))

:::warning
These routes are not available from the **production** environment, they only exists because there no Adage platform available from the **integration** environment.
:::

## July 2024

- You can now access your provider information using [**this endpoint**](/rest-api#tag/Providers/operation/GetProvider).
- You can now set your messaging URLs using the API. Futhermore you can now specify them a 2 levels: either at [**provider level**](/rest-api#tag/Providers/operation/UpdateProvider) or at [**venue level**](/rest-api#tag/Providers/operation/UpdateVenueExternalUrls).
- `enableDoubleBookings` field's default value is now `true` on event creation or update.

## June 2024

- You can now specify your own id when you [**create an individual event offe**r](/rest-api#tag/Event-Offers/operation/PostEventOffer) and/or [**create stock for this event**](/rest-api#tag/Event-Offer-Stocks/operation/PostEventStocks). This id is called `idAtProvider` and will be sent to your ticketing system when a beneficiary books a ticket ; in the message payload, it is called `offer_id_at_provider`.
- You can now specify you own id when you [**create stocks for an event offer**](/rest-api#tag/Event-Offer-Stocks/operation/PostEventStocks). This id called `idAtProvider` and will be sent to your ticketing system when a beneficiary books a ticket ; in the message payload, it is called `stock_id_at_provider`.

## March 2024

- Collective categories have been replaced by educational format to be more accurate. Collective categories will be definitively removed on September, the 31st 2024.

## February 2024

- New music types have been defined for musical events, CD and vinyls. We adopted Titelive classification. Older types will be definitively removed on September, the 31st 2024.

## January 2024

- Rate limiting has been implemented to the Pass Culture public API. **You are now limited to 200 requests/minute** per API key.
  Once this limit reached, you will received a `429 Too Many Requests` error message. You will then need to back down.
