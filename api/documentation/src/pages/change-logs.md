---
title: Pass Culture API change logs
---

# Change logs

:::info
Soon, a `bookingAllowedDatetime` parameter will be available at offer creation and update. Thanks to this new parameter, you will be able to specify when your offer becomes bookable.

You will have two dates at your disposal :

- a `publicationDatetime` that indicates the date and time when the offer becomes visible in the beneficiary application
- a `bookingAllowedDatetime` that indicates the date and time when the offer becomes bookable in the beneficiary application. If not set, the offer will be bookable as soon as it is published.
  :::

## January 2026

- You can now filter bookings either by `offerId` or `venueId` (endpoint: [**Get Bookings**](/rest-api#tag/Bookings/operation/GetBookings))
- `label` was added to the response payload of the [**Get Event categories endpoint**](/rest-api#tag/Offer-Attributes/operation/GetEventCategories)

## December 2025

- The `eventDuration` parameter for creating and updating event offers are now capped at 24 hours. To create or update events longer than 24 hours, you will need to leave this field empty.

## October 2025

- You can now add a `videoUrl` that comes from Youtube on your offers (endpoints : [**Create Event Offer**](/rest-api#tag/Event-Offers/operation/PostEventOffer), [**Update Event Offer**](/rest-api#tag/Event-Offers/operation/EditEvent)
- You can now filter offerers by New Caledonian RID7 on [**Get Offerer Venues**](/rest-api#tag/Venues/operation/GetOffererVenues) and fetch new caledonian venues by RIDET on [**Get Venue**](/rest-api#tag/Venues/operation/GetVenueBySiret)

## September 2025

- The new collective offer status `offerStatus` now determines which actions are allowed on the offer. You can find details on the new status and the allowed actions [here](/docs/understanding-our-api/resources/collective-offers#collective-offer-status-and-allowed-actions).
- Both `isActive` and `isSoldOut` fields have been removed from all collective endpoints.
- The `status` field has been removed from the following collective endpoints, the `offerStatus` field should be used instead:
  - [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic)
  - [**Get Collective Offers endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOffersPublic) (both in the query parameters and the response body)
  - [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic)
  - [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic)
- The `offerVenue` field has been removed from all collective endpoints. The `location` field must be used instead, and is now required in the request body of the [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic). You can find relevant information [here](/docs/understanding-our-api/resources/collective-offers#offers-location).
- Collective offers with `isActive = false` and no related booking have been archived. This does not apply to offers that are under review or rejected by the validation process.

## July 2025

- You can specify a `publicationDatetime` for your product offers in the [**Create Product Offer**](/rest-api#tag/Product-Offers/operation/PostProductOffer) and [**Update Product Offer**](/rest-api#tag/Product-Offers/operation/EditProduct) endpoints
- You can specify a `publicationDatetime` for your event offers in the [**Create Event Offer**](/rest-api#tag/Event-Offers/operation/PostEventOffer) and [**Update Event Offer**](/rest-api#tag/Event-Offers/operation/EditEvent) endpoints

## June 2025

- The number of price categories per offer is now limited to 50 (endpoints: [**Create Price Categories**](/rest-api#tag/Event-Offer-Price-Categories/operation/PostEventPriceCategories), [**Create Event Offer**](/rest-api#tag/Event-Offers/operation/PostEventOffer))
- The response of the following endpoints now includes 2 new fields, `offerAddress` and `offerDepartmentCode`, that replace respectively `venueAddress` and `venueDepartementCode`. These new fields are based on the offer location, whereas the previous fields displayed informations pertaining to the offer's venue location:
  - [**Get Booking endpoint**](/rest-api#tag/Bookings/operation/GetBookingByToken)
  - [**Get Bookings endpoint**](/rest-api#tag/Bookings/operation/GetBookings)

## May 2025

- The `offerVenue` attribute for collective offers is deprecated and will be removed in a future version. Please use the `location` attribute instead for specifying offer locations.
- The `isActive` field is now optional in the [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic). Calls to this endpoint should not provide this attribute anymore as it is deprecated.
- A new `location` attribute has been added to the request bodies of the [**Post Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic) and [**Patch Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic). The `offerVenue` attribute is now optional, you must provide either `location` or `offerVenue` when creating or updating a collective offer.
- The response of the following endpoints now includes a new `offerStatus` field (see details [here](docs/understanding-our-api/resources/collective-offers#collective-offer-status-and-allowed-actions)):
  - [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic)
  - [**Get Collective Offers endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOffersPublic)
  - [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic)
  - [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic)
- `offerStatus` is now also available as a query parameter in the [**Get Collective Offers endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOffersPublic) to retrieve only the offers with a given `offerStatus`.
- The response of the following endpoints now includes a new `location` field:
  - [**Get Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic)
  - [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic)
  - [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic)
- A new endpoint has been added to archive collective offers : [**Archive collective offers**](/rest-api#tag/Collective-Offers/operation/ArchiveCollectiveOffers). See the following for details on the different collective offer statuses [**here**](/docs/understanding-our-api/resources/collective-offers#collective-offer-status-and-allowed-actions).
- You can now specify a `description` that is up to 10 000 characters long (endpoints : [**Create Event Offer**](/rest-api#tag/Event-Offers/operation/PostEventOffer), [**Update Event Offer**](/rest-api#tag/Event-Offers/operation/EditEvent), [**Create Product Offer**](/rest-api#tag/Product-Offers/operation/PostProductOffer), [**Update Product Offer**](/rest-api#tag/Product-Offers/operation/EditProduct))

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

- You can now check if your EANs are available for bulk upsert using [**this endpoint**](/rest-api#tag/Product-Offer-Bulk-Operations/operation/CheckEansAvailability)

### Collective booking status (integration only)

It is possible to change the status of collective booking into the **integration** environment. We have created new endpoints to modify these statuses and simulate the booking timeline on the Adage side. Please check [rest api documentation](</rest-api#tag/Adage-Mock-(Collective-Bookings)>)

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
