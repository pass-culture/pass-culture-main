---
sidebar_position: 2
---

# Adage mocks

In the integration environment, it is possible to change the status of collective booking using the [**Adage mock endpoints**](/rest-api#tag/Adage-Mock-(Collective-Bookings)). Those endpoints simulate the actions coming from  Adage side.

:::info
Those actions are not available in the **production environment**.
They are available in the **integration environment** one because Adage is not available on it.
:::

## How to change the status of a collective booking in the integration environment ?

### Cancel a collective booking

- **What it mocks:** a collective booking being cancelled by the cultural partner.
- **Which endpoint:** [**Mock collective booking cancellation**](/rest-api#tag/Adage-Mock-(Collective-Bookings)/operation/AdageMockCancelCollectiveBooking)
- **Possible when:** booking status is `pending` or `confirmed`.

### Confirm a collective booking

- **What it mocks:** a collective booking being confirmed by the headmaster
- **Which endpoint:** [**Mock collective booking confirmation**](/rest-api#tag/Adage-Mock-(Collective-Bookings)/operation/ConfirmCollectiveBooking)
- **Possible when:** booking status is `pending`, `used` or `cancelled`.

### Use a collective booking

- **What it mocks:** a collective booking being used (it will the be reimbursed in the next payment, 48h after the event).
- **Which endpoint:** [**Mock collective booking being used**](/rest-api#tag/Adage-Mock-(Collective-Bookings)/operation/UseCollectiveBooking)
- **Possible when:** booking status is `confirmed` or `cancelled`.

### Reimburse a collective booking

- **What it mocks:** a collective booking being reimbursed by the pass Culture.
- **Which endpoint:** [**Mock collective booking being reimbursed**](/rest-api#tag/Adage-Mock-(Collective-Bookings)/operation/ReimburseCollectiveBooking)
- **Possible when:** booking status is `used`.

### Reset collective booking (back to pending)

- **What it mocks:** reset the collective booking's status
- **Which endpoint:** [**Mock collective booking reset**](/rest-api#tag/Adage-Mock-(Collective-Bookings)/operation/ResetCollectiveBooking)
- **Possible when:** booking status is neither `used` or `reimbursed`.
