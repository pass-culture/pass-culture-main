---
sidebar_position: 2
title: Managing countermarks
---

# Managing countermarks

For **`Products`** (and **`Events`** not linked to a ticketing system), bookings are countermarks that you can validate or cancel by calling our API.

## Notification

### Prerequisites

To be notified when a beneficiary books (or cancels a booking) a product (or an event not linked to a ticketing system), you need :

- to have the notification URL set (**[as explained here](/docs/understanding-our-api/notification-system/setting-up-notifcations)**)
- to have implemented the pass Culture notification authentication on your side (**[as explained here](/docs/understanding-our-api/notification-system/authenticating-our-notifications)**) 

### Our request payload

Each time a beneficiary books a product (or an event not linked to a ticketing system) or cancels his/her booking, you will receive a post request on your **notification URL** with the following payload :

#### JSON payload

```json
{
    "action": "BOOK",
    "booking_confirmation_date": "2022-10-14T17:09:25",
    "booking_creation_date": "2022-10-12T17:09:25",
    "booking_quantity": 1,
    "offer_ean": "9787547722909",
    "offer_id": 1234,
    "offer_name": "Le petit Prince",
    "offer_price": 1000,
    "price_category_id": 1234,
    "price_category_label": null,
    "stock_id": 1234,
    "user_birth_date": "2007-01-01",
    "user_email": "john.doe@test.com",
    "user_first_name": "john",
    "user_last_name": "doe",
    "user_phone": "+334123442231",
    "venue_address": "1 boulevard Poissonniere",
    "venue_department_code": "75",
    "venue_id": 12345,
    "venue_name": "Your bookshop",
}
```

#### JSON keys explanations

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **action** | **`BOOK`** or **`CANCEL`** | **`false`** | Type of action from the beneficiary (cancellation or booking) |
| **booking_confirmation_date** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | **`false`** | The booking confirmation date |
| **booking_creation_date** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | **`false`** | The booking creation date |
| **booking_quantity** | Integer | **`false`** | The number of items booked |
| **offer_ean** | String | `true` | Offer EAN code |
| **offer_id** | Integer | **`false`** | Offer id |
| **offer_name** | String | **`false`** | Offer name |
| **offer_price** | Integer | **`false`** | Offer price in euro and in cents (*for instance 1000 = 10 €*) |
| **price_category_id** | Integer | `true` | Not relevant for products (used for events) |
| **price_category_label** | String | `true` | Not relevant for products (used for events)  |
| **stock_id** | Integer | **`false`** | The stock id on our side |
| **user_birth_date** | Stringified date (format **`YYYY-MM-DD`**) | **`false`** | Beneficiary birth date |
| **user_first_name** | String | **`false`** | Beneficiary first name |
| **user_last_name** | String | **`false`** | Beneficiary last name |
| **user_phone** | String | `true` | Beneficiary phone |
| **venue_address** | String | **`false`** | Venue address |
| **venue_department_code** | String | **`false`** | Venue department code (*for instance 75*) |
| **venue_id** | Integer | **`false`** | Venue id |
| **venue_name** | String | **`false`** | Venue name |


## Understanding booking statuses

### Booking statuses for `products`

- A booking has the status **`CONFIRMED`** when **a beneficiary has booked a product offer and has not yet retrieved his/her product**
- A booking has the status **`USED`** when **the booking has been validated by the cultural partner** (meaning the beneficiary has retrieved the product)
- A booking has the status **`REIMBURSED`** when **the pass Culture has reimbursed the cultural partner for the booking** (the beneficiary has retrieved the product and the pass Culture has reimbursed the cultural partner)
- A booking has the status **`CANCELLED`** when :
  - **the beneficiary has cancelled his/her booking**
  - **the cultural partner has cancelled the booking**
  - **the booking has automatically been cancelled** because the beneficiary has not retrieve his/her booking in time (10 days)

### Booking statuses lifecycle for `products`

#### Step 1 : booking creation with the status **`CONFIRMED`**
The beneficiary books a product. It creates a booking with the status **`CONFIRMED`**.

#### Step 2 : booking validation (`CONFIRMED` -> `USED`) or booking cancellation (`CONFIRMED` -> `CANCELLED`) 
Here there are four possibilities :
- **The beneficiary retrieves its booking** within 10 days, **so you validate its booking** : the booking status is set to **`USED`**
- **The beneficiary cancels its booking** : the booking status is set to **`CANCELLED`**
- **You cancel the beneficiary's booking** : the booking status is set to  **`CANCELLED`**
- **The pass Culture cancels the beneficiary's booking** because he/she does not retrieve its booking within 10 days : the booking status is set to  **`CANCELLED`**

#### Step 3 : booking reimbursement (`USED` -> `REIMBURSED`)
Every two weeks, the pass Culture reimbursed the used bookings. The booking status is then set to **`REIMBURSED`**.

### Booking statuses for `events`

- A booking has the status **`CONFIRMED`** when **a beneficiary has booked a ticket for your event**
- A booking has the status **`USED`** when :
  - **the ticket has been validated by you (at the event)**
  - **the ticket has been automatically validated by the pass Culture 48 hours after your event date** 
- A booking has the status **`REIMBURSED`** when **the pass Culture has reimbursed the cultural partner for the ticket**
- A booking has the status **`CANCELLED`** when :
  - **the beneficiary has cancelled his/her ticket**
  - **the cultural partner (you) has cancelled the ticket**

### Booking statuses lifecycle for `events`

#### Step 1 : booking creation with the status **`CONFIRMED`**
The beneficiary books a ticket for your event. It creates a booking with the status **`CONFIRMED`**.

#### Step 2 : booking validation (`CONFIRMED` -> `USED`) or booking cancellation (`CONFIRMED` -> `CANCELLED`) 

*Option 1 - Booking cancellation (**`CONFIRMED`** -> **`CANCELLED`**)*

A booking can be cancelled, i.e. its status set to **`CANCELLED`**, in three cases :
-  **by you**, until 48 hours before the event
-  **by the beneficiary** :
   -  **if the beneficiary booked its ticket more than two days before the event**, the beneficiary has the possibility to cancel its ticket **within the 48 hours following his/her booking** (otherwise, it is a last minute booking and it is not cancellable)
   -  **if you change your event date**, the beneficiary has the possibility to cancel its ticket :
      -  if your new event date is in **less** than two days, **until your event date**
      -  if your new event date is in **more** than two days, **within the 48 hours following your change**

*Option 2 - Booking validation (**`CONFIRMED`** -> **`USED`**)*

A booking is validated, i.e. its status set to **`USED`** :

- either **automatically by the pass Culture**, **48 hours after your event**
- either **by you**, at the event **[by calling the validation endpoint](#countermark-validation)**


#### Step 3 : booking reimbursement (`USED` -> `REIMBURSED`)
Every two weeks, the pass Culture reimbursed the used bookings. The booking status is then set to **`REIMBURSED`**.


## Countermark validation

To validate a countermark (i.e. a booking) presented by a beneficiary, **you need to do a PATCH request [on this URL](/rest-api#tag/Booking/operation/ValidateBookingByToken)**.

### ✅ Success 
If the countermark is found, and hasn't yet been used (i.e. if its status is **`CONFIRMED`**), then **we will return a `HTTP 204` response**, indicating that **the countermark has been successfully validated**. The countermark status will then change to **`USED`**.

### 🚫 Errors 
You can expect **three kinds of errors** when trying to validate a countermark (i.e. a booking) on our servers.


#### `HTTP 403` : The booking has been reimbursed or is a cancellable event ticket

You will get an **`HTTP 403`** from our side if you try to validate a countermark (i.e. a booking):

- that has the status **`REIMBURSED`**, meaning it has already been used and you have been reimbursed for it by the pass Culture.
- **(in the case of event booking)** that can still be cancelled by the beneficiary ([**see above**](#booking-statuses-lifecycle-for-events))

#### `HTTP 404` : The booking has not been found

You will get an **`HTTP 404` response** from our side :

- if **the booking does not exist** on our side
- if you are trying to validate **a booking you are not allowed to access to**

#### `HTTP 410` : The booking has been cancelled or has already been used

You will get an **`HTTP 410`** from our side if you try to validate a countermark (i.e. a booking):

- that has the status **`USED`**, meaning it **has already been validated**
- that has the status **`CANCELLED`**, meaning that either you, the beneficiary or the pass Culture, **has cancelled the booking before it was used**


## Countermark cancellation

To cancel a countermark (i.e. a booking), **you need to do a PATCH request [on this URL](/rest-api#tag/Booking/operation/CancelBookingByToken)**.

### ✅ Success 
If the countermark is found, and hasn't yet been used (i.e. if its status is **`CONFIRMED`**), then **we will return a `HTTP 204` response**, indicating that **the countermark has been successfully cancelled**. The countermark status will then change to **`CANCELLED`**.

### 🚫 Errors
You can expect **three kinds of errors** when trying to cancel a countermark (i.e. a booking) on our servers.


#### `HTTP 403` : The booking has been reimbursed or is a cancellable event ticket

You will get an **`HTTP 403`** from our side if you try to validate a countermark (i.e. a booking) that has the status **`REIMBURSED`**, meaning it has already been used and you have been reimbursed for it by the pass Culture.

#### `HTTP 404` : The booking has not been found

You will get an **`HTTP 404` response** from our side :

- if **the booking does not exist** on our side
- if you are trying to cancel **a booking you are not allowed to access to**

#### `HTTP 410` : The booking has been cancelled or has already been used

You will get an **`HTTP 410`** from our side if you try to cancel a countermark (i.e. a booking):

- that has the status **`USED`**, meaning it **has already been validated**
- that has the status **`CANCELLED`**, meaning that either you, the beneficiary or the pass Culture, **has cancelled the booking before it was used**