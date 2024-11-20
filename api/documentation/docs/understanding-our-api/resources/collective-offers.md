---
sidebar_position: 2
---
# Collective offers

**Collectives offers** are **events meant for scholar groups**. They can be managed using the **[collective offers endpoints](/rest-api#tag/Collective-Offers)**. These offers will be displayed by the Adage platform (which is not run by the pass Culture team).

This public API offers some (basic) functionality in order to handle collective offers and their bookings.

## General description

There are two objects to manage collective offers: offer templates and bookable offers. The first are meant to explain what could be done, the latter when and how. Teachers will search for templates and open a discussion with the cultural partner, which will make a proposal in return: the bookable offer.

:::info
Please note that templates and book offers are two distinct objects: a template offer's data will be copied into a bookable one's. This means that they will have distinct database IDs.
:::

A bookable offer is linked to (at least) one collective booking. Most of the time, there is only one booking for one offer. However, if a booking is cancelled, a new one can be created. In that case, the offer has two bookings: an ongoing one and a cancelled one.

:::info
There can only be one active booking per bookable offer.
:::

### Who can view and book collective offers?

A collective offer is visible :

- to a cultural partner once it has been created on the pass Culture application
- to a teaching staff member on the Adage platform

Collective offers are not visible on the pass Culture application for beneficiaries.

### Administrative/billing address

A collective offer is always linked to an administrative venue: its the `venueId` field.

### Status

A bookable offer can have five states:

* `PENDING`
* `CONFIRMED`
* `USED`
* `CANCELLED`
* `REIMBURSED`

`PENDING` means it has been proposed to the teacher. Once both sides are ok with the price, details, etc. it becomes `CONFIRMED`. It becomes `USED` when the event is passed and, finally, it becomes `REIMBURSED` after a short period of time (check the official documentation to get more detailed financial information). If the offer is cancelled... it becomes `CANCELLED`, obviously.

### Offer location

A collective offer is always linked to an administrative venue: its the `venueId` field. However it can take place at an address other than the venue address.

There are two location types: at school or elsewhere. For the latter, there are two ways to specify the location: either using a venue's id (from our database, usually one of your venue), or using a free text field.

The location must be specified under the `offerVenue` object which contains three fields:

* `addressType` (`OFFERER_VENUE`, `SCHOOL` or `OTHER`);
* `venueId` (`null` when type is `SCHOOL` or `OTHER`);
* `otherAddress` (not `null` only if `addressType` equals `OTHER`).

:::warning
`offerVenue` defines where the event takes place, `venueId` defines the administrative/billing address.
:::

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

Only `PENDING` offers can be updated.
An offer created using the public API cannot be edited using the PRO web portal.

## Collective bookings

A collective booking is linked to a collective offer and works for a group of students.

:::info
Meaning: if a school project is booked for a 30 students class, there will be only one booking, not thirty.
:::

Also, the validation process is not the same as individual offers since these offers are meant to be a part of a larger school/teaching project.