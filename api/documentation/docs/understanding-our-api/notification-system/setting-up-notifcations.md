---
sidebar_position: 1
description: How to set up notifications from the pass Culture application
---

# Setting up notifications

The pass Culture provides a **webhook system** that has a **double purpose** :

- **notify** your servers **when a beneficiary books a `product`**
- **create/cancel tickets** in real time **when a beneficiary books a seat to an `event` linked to a ticketing server**

## Providing us with your notification URLs

In order to be able to manage the bookings coming from the pass Culture application, **you will need to provide us with URLs on which we will send you notifications**.

### The different kind of notification URLs

For `Products` (and `Events` not linked to a ticketing server), we will need **one notification URL**.

For `Events` linked to a ticketing server, we will need **two URLs** :

- **a booking URL** : to create a ticket on your side, and send it back to the beneficiary when a beneficiary book a ticket
- **a cancellation URL** : to cancel a ticket if the beneficiary cancels its booking

:::warning
The notification URLs you give us ***must not* require authentication**.

The notification authentication will be done by checking the request payload as described here : [**Authenticating our notifications**](/docs/understanding-our-api/notification-system/authenticating-our-notifications).
:::

### How to set the URLs

At the moment, those URLs are set manually by our support team.
For your notification URLs to be set, [**you need to send an email to our support team**](mailto:partenaires.techniques@passculture.app).

:::warning
Do not forget to give **one URL per environment**.

*For instance, if you are developing an integration linked to a ticketing system, you will need to provide our support team with four URLs:*
- *a booking URL and a cancellation URL for the **integration test environment***
- *a booking URL and a cancellation URL for the **production environment***
:::
