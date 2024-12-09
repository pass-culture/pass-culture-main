---
sidebar_position: 2
---

# Adage mocks

It is possible to change the status of collective booking into the integration environment. We have created new endpoints to modify these statuses and simulate the booking timeline on the Adage side.

:::warning
Theses actions are not available from the **production** environment.
They are available from the **integration** one because Adage is not available from it.
:::

## How to change the status of a collective booking in an integration environment ?

### cancel a collective booking

Mocks: the collective booking has been cancelled by the cultural partner.

route: POST `/v2/collective/adage_mock/bookings/{booking_id}/cancel`.

Action is possible if booking is pending or confirmed.

### confirm a collective booking

Mocks: the collective booking has been confirmed by the headmaster.

route: POST `/v2/collective/adage_mock/bookings/{booking_id}/confirm`

Action is possible if booking is pending, used or cancelled.

### use a collective booking

Mocks: the booking has been used and will be reimbursed in the next payment (48h after the collective event).

route: POST `/v2/collective/bookings/{booking_id}/use`

Action is possible if booking has a confirmed or canceled status.

### reimburse a collective booking

Mocks: the booking has been reimbursed by pass Culture to the venue.

route: POST `/v2/collective/adage_mock/bookings/{booking_id}/reimburse`

Action is possible if the booking has been used.

### reset collective booking (back to pending)

Mocks : the booking status has been reset.

route: POST `/v2/collective/adage_mock/bookings/{booking_id}/pending`

Action is possible if the collective booking is neither used nor reimbursed (and can be cancelled).
