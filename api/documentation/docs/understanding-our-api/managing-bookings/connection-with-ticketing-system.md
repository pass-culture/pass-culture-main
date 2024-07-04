---
sidebar_position: 1
---

# Connection with a ticketing system

If you have a ticketing system to manage your events tickets, it is possible to connect your ticketing system with the pass Culture application.

## Mandatory set-up

To connect your ticketing system to the pass Culture application, you need first:

1. **To provide us with a booking and a cancelling URL** that we will request each time a beneficiary book/cancel a ticket for the event. You can find the process **[here](/docs/understanding-our-api/notification-system/setting-up-notifcations)**.
2. **To implement the notification authentication process** described **[here](/docs/understanding-our-api/notification-system/authenticating-our-notifications)** on your side.

## Enable ticket booking for an event

Once your provider account is properly set (with a booking URL and a cancellation URL), you can enable ticket booking for an event by **setting the `hasTicket` parameter to `true`** when **[creating the event](/rest-api#tag/Event-offers/operation/PostEventOffer)**.

:::note
Once the event is created, you cannot change the **`hasTicket`** attribute.
:::

## Ticket booking process 

### General explanation

If you enabled ticket booking for an event, we will call **your booking URL** whenever a beneficiary books a ticket for this event on the pass Culture application.
We will wait for your response, that must contain a barcode, and forward it to the beneficiary.

:::warning
As it is a **synchronous process**, we will display an error to the beneficiary :
- if **your response doesn't match the expected format**
- if **your server takes to long (more than ten seconds) to respond** to our request.
:::

### 📩 Our request payload

We will be calling your booking URL with the following payload :

#### JSON payload example
```json
{
    "booking_confirmation_date": "2022-10-14T17:09:25",
    "booking_creation_date": "2022-10-12T17:09:25",
    "booking_quantity": 1,
    "offer_ean": "1234567890123",
    "offer_id": 1234,
    "offer_name": "Mon offre",
    "offer_price": 1000,
    "price_category_id": 1234,
    "price_category_label": "Ma cat de prix",
    "stock_id": 1234,
    "user_birth_date": "2007-01-01",
    "user_email": "test@test.com",
    "user_first_name": "john",
    "user_last_name": "doe",
    "user_phone": "+334123442231",
    "venue_address": "1 boulevard Poissonniere",
    "venue_department_code": "75",
    "venue_id": 12345,
    "venue_name": "Mon lieu trop cool",
}
```

#### JSON keys explanations

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **booking_confirmation_date** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | **`false`** | The booking confirmation date |
| **booking_creation_date** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | **`false`** | The booking creation date |
| **booking_quantity** | Integer | **`false`** | The number of tickets, either 1 or 2 (if you set **`enableDoubleBookings`** to `true` [**when creating the event**](/rest-api#tag/Event-offer/operation/PostEventOffer)) |
| **offer_ean** | String | `true` | Offer EAN code (relevant for product) |
| **offer_id** | Integer | **`false`** | Offer id |
| **offer_name** | String | **`false`** | Offer name |
| **offer_price** | Integer | **`false`** | Offer price in euro and in cents (*for instance 1000 = 10 €*) |
| **price_category_id** | Integer | `true` | The price category id (cannot be null in the case of an event) |
| **price_category_label** | String | `true` | The price category label (*for instance, "Catégorie Or"*) |
| **stock_id** | Integer | **`false`** | The stock id on our side |
| **user_birth_date** | Stringified date (format **`YYYY-MM-DD`**) | **`false`** | Beneficiary birth date |
| **user_first_name** | String | **`false`** | Beneficiary first name |
| **user_last_name** | String | **`false`** | Beneficiary last name |
| **user_phone** | String | `true` | Beneficiary phone |
| **venue_address** | String | **`false`** | Event venue address |
| **venue_department_code** | String | **`false`** | Event venue department code (*for instance 75*) |
| **venue_id** | Integer | **`false`** | Event venue id |
| **venue_name** | String | **`false`** | Event venue name |



### ✅ Success response

In case of success, here is the JSON we expect in return :

#### JSON payload example

```json
{
	"remainingQuantity": 12,
	"tickets" : [{
		"barcode": "1234567AJSQ",
		"seat": "A12"
		},{
		"barcode": "1234567AJSA",
		"seat": "A14"},
	}]
}
```

#### JSON keys explanation

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **remainingQuantity** | Integer | **`false`** | Number of tickets still available after this booking (for us to update our stock) |
| **tickets** | Array | **`false`** | Booked tickets (should contain one or two items) |
| **tickets[].barcode** | String | **`false`** | Ticket barcode **(⚠️ mandatory)** |
| **tickets[].seat** | String | `true` | Ticket seat |

### 🚫 Error responses

There are two cases for which we are expecting an error when we try to book a ticket on your server :

- the event date is **sold-out**
- we are trying to book 2 tickets but **there is only one ticket left** 

In those cases, **we expect from you a `HTTP 409` response with the following payload** :

#### JSON payload example

```json
{
    "error": "not_enough_seats",
    "remainingQuantity": 1
}
```

#### JSON keys explanation

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **error** | `not_enough_seats` or `sold_out` | **`false`** | Error code |
| **remainingQuantity** | Integer | **`false`** | Number of tickets still available (should be `1` for `not_enough_seats` and `0` for `sold_out`) |


## Ticket cancellation process 

### General explanation
If a beneficiary has booked a ticket for your event but decides to cancel it, we will call your **cancellation URL** with the cancelled barcodes.

### 📩 Our request payload

We will be calling your **cancellation URL** with the following payload :

#### JSON payload example
```json
{
    "barcodes" : [
        "1234567AJSQ", 
        "1234567AJSA"
    ]
}
```

#### JSON keys explanation

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **barcodes** | Array | **`false`** | List of ticket barcodes (contains one or two barcode) |
| **barcodes[]** | String | **`false`** | Ticket barcode generated by your ticketing system |


### ✅ Expected response

When cancelling tickets on your server, if the request is successful, we expect the following response in return :


#### JSON payload example
```json
{
    "remainingQuantity" : 45
}
```

#### JSON keys explanation

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **remainingQuantity** | Integer | `true` | If the remaining stock is unlimited, you should return `null` |

