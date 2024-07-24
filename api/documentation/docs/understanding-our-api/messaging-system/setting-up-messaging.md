---
sidebar_position: 1
description: How to set up messaging to receive messages from the pass Culture application
---

# Setting up messaging

The pass Culture provides a **messaging system** that has a **double purpose** :

- **notify** your servers **when a beneficiary books a `product`**
- **create/cancel tickets** in real time **when a beneficiary books a seat to an `event` linked to a ticketing server**

:::info
**Notification messages** are **asynchronous**.

On the other hand, **ticket cancellation** or **ticket creation messages** are **synchronous** and requires a reasonably fast response from your server (no more than 8 seconds).
:::

## Providing us with your messaging URLs

In order to be able to manage the bookings coming from the pass Culture application, **you will need to provide us with URLs on which we will send you messages**.

### The different kind of messaging URLs

For `Products` (and `Events` not linked to a ticketing server), we will need **one notification URL**.

For `Events` linked to a ticketing server, we will need **two URLs** :

- **a booking URL** : to create a ticket on your side, and send it back to the beneficiary when a beneficiary book a ticket
- **a cancellation URL** : to cancel a ticket if the beneficiary cancels its booking

:::warning
The messaging URLs you give us ***must not* require authentication**.

The message authentication will be done by checking the request payload as described here : [**Authenticating our messages**](/docs/understanding-our-api/messaging-system/authenticating-our-messages).
:::

### How to set the URLs

You can set those URLS at two levels :

- At **provider level**, using [**this endpoint**](/rest-api#tag/Providers/operation/UpdateProvider)
- At **venue level**, using [**this endpoint**](/rest-api#tag/Providers/operation/UpdateVenueExternalUrls)

For messages regarding offers (either `Events` or `Products`) you created using the API, we will first look if there is a URL defined at venue level.
If so, we will send you a message on this URL.
Otherwise, we will look if there is a URL defined at provider level and, if it is the case, send you a message on this second URL.

:::note
**We recommend defining URLs at provider level**. Define URLs at venue level only if the URLs vary from one venue to the other.
:::
