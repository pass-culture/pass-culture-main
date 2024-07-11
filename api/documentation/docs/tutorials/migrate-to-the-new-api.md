---
sidebar_position: 3
---

# Migrate to the new API

This tutorial is meant for providers who were using the old stocks and bookings APIs (endpoints starting with `/v2/bookings` and `/v2/venue/<venue_id>/stocks`) and need to migrate to the new API.

## Prerequisites

One of the main changes is that, on the old APIs, the API key was authenticating a offerer, whereas on the new API, the API key is authenticating a provider.

Therefore, to be able to migrate from the old endpoints to the new ones, you need:
- to **have a provider account** and **an API key to authenticate yourself as this provider** (see [**Request a provider**](/docs/mandatory-steps/request-a-provider-account))
- to **have been given access to the venues** by the offerers (see [**Authentication & Authorization**](/docs/understanding-our-api/authentication-authorization))

## Migrating to the new bookings endpoints

To migrate your existing integration to the new bookings endpoints, you need:

First, **to authenticate your calls using your provider API key**, instead of the old API key given by the offerer.

Then, to make the following changes:
* Replace **GET** `/v2/bookings/token/<token>` with **GET** `/public/bookings/v1/token/<string:token>` ([**endpoint documentation**](/rest-api#tag/Bookings/operation/GetBookingByToken))

* Replace **PATCH** `/v2/bookings/use/token/<token>` with **PATCH** `/public/bookings/v1/use/token/<token>` ([**endpoint documentation**](/rest-api#tag/Bookings/operation/ValidateBookingByToken))

* Replace **PATCH** `/v2/bookings/cancel/token/<token>` with **PATCH** `/public/bookings/v1/cancel/token/<token>` ([**endpoint documentation**](/rest-api#tag/Bookings/operation/CancelBookingByToken))

* Replace **PATCH** `/v2/bookings/keep/token/<token>` with **PATCH** `/public/bookings/v1/keep/token/<token>` ([**endpoint documentation**](/rest-api#tag/Bookings/operation/CancelBookingValidationByToken)).

:::warning
Using the `/public/bookings/v1/keep/token/<token>` endpoint can lead to integrations with unwanted behaviors.
**Please make sure that when you call this endpoint, your user has confirmed he/she wanted to cancel the booking validation.** Otherwise, we might end up in a situation where the user is confused because he/she expects a reimbursement from the pass that never comes (as we consider that the booking was not validated).
:::

 ## Migrating to the new stocks endpoint

To migrate your existing integration to the [**new stocks management endpoint**](/rest-api#tag/Product-offer-bulk-operations/operation/PostProductOfferByEan), you need:

First, **to authenticate your calls using your provider API key**, instead of the old API key given by the offerer.

Then, to update the endpoint you call: replace **POST** `/v2/venue/<venue_id>/stocks` with **POST** `/public/offers/v1/products/ean`.

Finally, to update the payload you are sending us:

**Previous payload**
```json
{
    "stocks": [
        {
            "ref": "<your_product_ean>",
            "price": "<your_product_price>",
            "available": "<your_product_quantity>"
        }
    ]
}
```

**Updated payload**
```json
{
    "location": {
        "type": "physical",
        "venueId": "<the_venue_id>"
    },
    "products": [
        {
            "ean": "<your_product_ean>",
            "stock": {
                "price": "<your_product_price>",
                "quantity": "<your_product_quantity>"
            }
        }
    ]
}
```

:::info
The new endpoint offers you the possibility to indicate a `bookingLimitDatetime` in the stock parameters. The `bookingLimitDatetime` is the date after which it is not possible to book the product.
:::
