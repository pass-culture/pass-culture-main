---
sidebar_position: 2
---
# Collective offers

**Collectives offers** are **events meant for scholar groups**. They can be managed using the **[collective offers endpoints](/rest-api#tag/Collective-Offers)**. These offers will be displayed by the Adage platform (which is not run by the pass Culture team).

This public API offers some (basic) functionality in order to handle collective offers and their bookings.

## General description

There are two objects to manage collective offers: offer templates and bookable offers. The first are meant to explain what could be done, the latter when and how. Teachers will search for templates and open a discussion with the cultural partner, which will make a proposal in return: the bookable offer.

:::info
Please note that templates and bookable offers are two distinct objects: a template offer's data will be copied into a bookable one's. This means that they will have distinct database IDs.

⚠️ The templates are only managed on the pro interface, not via API.
:::

A bookable offer is linked to (at least) one collective booking. Most of the time, there is only one booking for one offer. However, if a booking is cancelled, a new one can be created. In that case, the offer has two bookings: an ongoing one and a cancelled one.

:::info
There can only be one active booking per bookable offer.
:::

### Who can view and book collective offers?

A collective offer is visible:

- to a cultural partner once it has been created on the pass Culture application
- to a teaching staff member on the Adage platform

Collective offers are not visible on the pass Culture application for beneficiaries.

### Administrative/billing address

A collective offer is always linked to an administrative venue: its the `venueId` field.

### Offers created by Pro interface users vs. API users

It can happen that the **`venue`** is managed both **via API** and **by a human user using the pro interface**. In this case, according to whom has created the collective offer, the API user or the Pro interface user might be limited to a certain set of actions on the collective offer.

#### Case #1: the collective offer has been created via API

If a collective offer has been created using the API, it is visible on the Pro interface, however, the human user is only allowed to perform a limited set of actions on the collective offer:

- Archive the offer
- Duplicate the offer

#### Case #2: the collective offer has been created on the pro interface

If a collective offer has been created by a user on the pro interface, then it is not possible to modify it by API.

### Booking Status

A collective offer, when created, does not have any related booking. Once the teacher has pre-booked the offer, a booking object is created.

A collective booking can have five statuses:

* `PENDING`
* `CONFIRMED`
* `USED`
* `CANCELLED`
* `REIMBURSED`

`PENDING` means it has been proposed to the teacher.

Once both sides are ok with the price, details, etc. the school headmaster confirms the booking and it becomes `CONFIRMED`.

It becomes `USED` two days after the event is passed.

Finally, it becomes `REIMBURSED` after a short period of time (check the official documentation to get more detailed financial information).

If the offer is cancelled either by the school or using the [Cancel Collective Booking endpoint](/rest-api#tag/Collective-Bookings/operation/CancelCollectiveBooking), it becomes `CANCELLED`.

## Creation rules

### Offer templates

One cannot create a collective offer template using the public API.

### Bookable offers

:::warning
To be able to create a bookable offer, your offerer must be referenced by Adage.
:::

A bookable offer can be created using the [Create Collective Offer endpoint](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic).

## Update rules

### Offer templates

They cannot be updated using the API.

### Bookable offers

A bookable offer can only be updated if there is no related collective booking, or if the booking is in the `PENDING` status.

Additionally, if the booking is `CONFIRMED`, the price can still be updated but only with a lower value. The number of students and the price details can also be updated.

An offer created using the public API cannot be edited using the PRO web portal.

## Collective bookings

A collective booking is linked to a collective offer and works for a group of students.

:::info
Meaning: if a school project is booked for a 30 students class, there will be only one booking, not thirty.
:::

Also, the validation process is not the same as individual offers since these offers are meant to be a part of a larger school/teaching project.

## Collective offer status and allowed actions

### ⚠️ Upcoming changes

A collective offer can have different statuses, depending on the event dates and the related booking status. You can check the current possible status values in the [Get Collective Offer endpoint response schema](/rest-api#tag/Collective-Offers/operation/GetCollectiveOfferPublic) -> `status` field.

:::warning
The collective offer status will be changed in the coming months. You can find below the new statuses list.

To allow the migration, this new status is available in the dedicated attribute `offerStatus`.

In addition, the offer status will determine the actions that are allowed on the offer (which fields can be updated, whether the booking can be cancelled...). You can find below a table showing which actions are allowed for each new status.
:::

- **DRAFT**: the offer is not yet published. Currently an offer created with the API cannot have this status
- **UNDER_REVIEW**: the offer is waiting to be reviewed and validated
- **PUBLISHED**: the offer is published and visible on the Adage platform
- **REJECTED**: the offer was not validated
- **PREBOOKED**: the offer has been pre-booked by the teacher
- **BOOKED**: the school headmaster has confirmed the pre-booking
- **EXPIRED**: the booking limit date has passed and the offer was not confirmed
- **ENDED**: the offer was confirmed and the end date has passed
- **REIMBURSED**: the offer has been reimbursed
- **CANCELLED**: 1. the offer has been cancelled by the school or with the API, or 2. the offer has not been confirmed before the offer start date
- **ARCHIVED**: the offer has been archived (this is currently only possible on the pro interface). It will not be visible on Adage

Here are the allowed actions depending on the offer status:

|Status           |Edit the details (title, description...) and increase the price|Edit the dates (start, end, booking limit) |Edit the institution |Edit the number of students, price details and lower the price |Duplicate the offer |Cancel the offer |Archive the offer|
|-----------------|:-:|:--:|:--:|:-:|:--:|:--:|:--:|
|**DRAFT**        | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
|**UNDER_REVIEW** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
|**PUBLISHED**    | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
|**REJECTED**     | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
|**PREBOOKED**    | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
|**BOOKED**       | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
|**EXPIRED**      | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
|**ENDED** (\<48h)| ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
|**ENDED** (\>48h)| ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
|**REIMBURSED**   | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
|**CANCELLED**    | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
|**ARCHIVED**     | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

### Current state of developments

Those limitations are currently enforced **only** on the following endpoints:

* [**Archive collective offers**](/rest-api#tag/Collective-Offers/operation/ArchiveCollectiveOffers)

The new status is available in the `offerStatus` field.

## 📍 Offers location

### Current offer location (⚠️ DEPRECATED)

:::warning
The `offerVenue` field will be replaced with the `location` field in the coming months. See the next section [here](/docs/understanding-our-api/resources/collective-offers#general-description-1) for details on the new `location` field.
:::

A collective offer is always linked to an administrative venue: its the `venueId` field. However it can take place at an address other than the venue address.

There are two location types: at school or elsewhere. For the latter, there are two ways to specify the location: either using a venue id (from our database, usually one of your venue), or using a free text field.

The location must be specified under the `offerVenue` object which contains three fields:

* `addressType` (`OFFERER_VENUE`, `SCHOOL` or `OTHER`);
* `venueId` (`null` when type is `SCHOOL` or `OTHER`);
* `otherAddress` (not `null` only if `addressType` equals `OTHER`).

:::warning
`offerVenue` defines where the event takes place, `venueId` defines the administrative/billing address.
:::

### General description

Collective offers are geotagged in Adage application using their location.

You can specify a collective offer's location:

- At creation: [**Create Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic)
- At update: [**Update Collective Offer endpoint**](/rest-api#tag/Collective-Offers/operation/PatchCollectiveOfferPublic)

:::warning
`location` defines where the event takes place, `venueId` defines the administrative/billing address.
:::

### Location types

The offer's location is specified using the `location` field, which supports three types:

#### 1. Location of type `ADDRESS`

There are two different cases of `ADDRESS` location.

* `"isVenueAddress" = true`

An `ADDRESS` location with `"isVenueAddress" = true` indicates that **the offer shares the same address as the venue**. This is common for cultural partners to organize an event where the offer's location matches the venue's location.

Example of the `location` field for type `ADDRESS` and `isVenueAddress = true`:
```json
{
  "type": "ADDRESS",
  "isVenueAddress": true
}
```

* `"isVenueAddress" = false`

:::tip
You can manage addresses using the [**Addresses endpoints**](/rest-api#tag/Addresses)
:::

An `ADDRESS` location with `"isVenueAddress" = false` indicates that **the offer’s address differs from the venue’s address**.

Example of the `location` field for type `ADDRESS` and `isVenueAddress = false`:
```json
{
  "type": "ADDRESS",
  "addressId": 1,
  "addressLabel": "Mon théâtre",
  "isVenueAddress": false
}
```

#### 2. Location of type `SCHOOL`

A `SCHOOL` location indicates that the offer takes place inside the educational institution.

Example of the `location` field for type `SCHOOL`:
```json
{
  "type": "SCHOOL"
}
```

#### 3. Location of type `TO_BE_DEFINED`

A `TO_BE_DEFINED` location indicates that the offer location is not precisely defined. The `comment` field can be filled in this case.

Example of the `location` field for type `TO_BE_DEFINED`:
```json
{
  "type": "TO_BE_DEFINED",
  "comment": "Will be clarified later"
}
```
