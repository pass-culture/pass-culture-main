---
sidebar_position: 1
---

# Individual offers

**Indivual offers** are offers **meant for individual beneficiary**. They are split in two main categories : **`products`** and **`events`**.

## 📚 `Products` 

:::tip
To manage those offers you will be mainly using the **[product offers endpoints](/rest-api/#tag/Product-offers)**.
:::

### General description

**`Products`** are cultural goods that are not linked to a date. They can be :
- **physical** : _for instance a book or or a CD_
- **digital** : _for instance a subscription to a music streaming service_

### Creation rules

There are **two methods to create a product offer** using the pass Culture API :

- **if your product is a book, a CD or a Vinyl**, you must create your product offer by indicating an **[European Article Numbering code (EAN)](https://en.wikipedia.org/wiki/International_Article_Number)**, a price and a quantity. We will fill the other offer fields using external databases (provided by our partner Titelive). The dedicated endpoint to upsert (create or update) product using EANs is **[this one](/rest-api/#tag/Product-offer-bulk-operations/operation/PostProductOfferByEan)**.
- **for others products**, you create your product offer by providing all the data. The dedicated endpoint for this kind of creation is **[this one](/rest-api/#tag/Product-offers/operation/PostProductOffer)**.

:::info
To be able to create a product offer using an EAN code, **this EAN code must exists in the pass Culture database**.

**It should not be an issue in production**, since we are using a professional service to get EAN codes. In the test in the integration test environment however, we have only a small set of EAN codes available. **[You can find the EAN codes here](/docs/test-data)**.
:::

### Update rule

Regardless of how your product offer was created, you can update it using **[this endpoint](/rest-api/#tag/Product-offers/operation/EditProduct)**. However, if you only need to update the product offer stock for a book, CD, or vinyl, you should use the **[batch upsert endpoint](/rest-api/#tag/Product-offer-bulk-operations/operation/PostProductOfferByEan)**.

### Concurrent access rules: Pro interface users vs. API users

It can happen that the **`venue`** is managed both **via API** and **by a human user using the pro interface**. 
In this case, according to whom has created the offer, the API user or the Pro interface user might be limited to a certain set of actions on the offer.

#### Case #1: the product offer has been created via API

If a product offer has been created using the API, it is visible on the Pro interface, however, the human user is only allowed to perform a limited set of actions on the offer :

- Deactivate/active the offer
- Update the accessibility conditions
- Update the public link
- Delete the stock (this will delete the bookings linked to this stock)

#### Case #2: the product offer has been created on the pro interface

If a product offer has been created by a user on the pro interface, then it is not possible to modify it by API. The only available action by API is : active/deactivate the offer.



## 🎭 `Events`

:::tip
To manage those offers you will be mainly using the **[event offers endpoints](/rest-api/#tag/Event-offers)**.
:::

### General description

`Events` are **cultural goods whose stocks are linked to a date and a price category**. 

:::note
For instance, an event can be "Le Bourgeois gentilhomme" at la Comédie Française.

This play can have several performances and for each performance they can be several price categories ("Carré or", "Catégorie 1"...). 

Therefore, you will have **`(number of performances)*(number of categories)`** stocks linked to this event.
:::

`Events` can be :
- **physical:** _for instance a concert or a theater performance_
- **digital:** _for instance a online painting lesson_


### Creation rules

Creating a `event` offer with its stocks is a three steps process.
You will need to first **[create the event](/rest-api/#tag/Event-offers/operation/PostEventOffer)**, then to **[create its price categories](/rest-api/#tag/Event-offer-prices/operation/PostEventPriceCategories)** and finally to **[create its stocks](/rest-api/#tag/Event-offer-stocks/operation/PostEventStocks)**.

Here are the rules you should be aware of when creating an event:
- the **number of price categories for an event** is limited to **`10`**
- the **number of dates for an event** is limited to **`10 000`**


## ⚡️ `Bookings`

:::tip
To manage those offers you will be using the **[bookings endpoints](/rest-api/#tag/Bookings)**.
:::

### General description

The **`booking`** is a resource shared by **`event` and `product` offers**.
A **`booking`** is a reservation made by a beneficiary of a product or of an event date.

### `Booking` for `products` 

**For a `product`**, the **`booking`** is a **🪙 countermark**. This **countermark** will be used by the beneficiary either:
- **in the case of a physical product**, to retrieve its order in the offerer shop. 

  _For instance, if you are developing a stock management systems for bookshops, the seller will validate the beneficiary order by inputting the countermark in your software. Your software will then make a call to our [booking validation endpoint](/rest-api/#tag/Bookings/operation/ValidateBookingByToken)_
- **in the case of a digital product**, to retrieve its order on the offerer website. 

  _For instance, if you are a music streaming service, the beneficiary will validate its order by inputting the countermark in one of the field of the offer website form. On the form submission, your website will make a call to our [booking validation endpoint](/rest-api/#tag/Bookings/operation/ValidateBookingByToken)_.

### `Booking` for `events` 

**For an `event`**, the **`booking`** is a **📅 reservation** for the event. **It can be linked to a ticket** if you plugged your [ticketing solution to the pass Culture application](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system)].

### Booking status

* `CONFIRMED` The bookings is confirmed. → the beneficiary has booked an offer but he didn’t pick it up
    * 📍 For a physical offer, until his token’s approval, beneficiary can cancel his booking.
        * he has 10 days to get his booking back if it’s a book → otherwise, automatic cancelation
        * He has 30 days to get it back for other physicals products → otherwise, automatic cancelation
    * 📍 For an event, pass Culture’s beneficiary has 48h to cancel an event booking, unless the `beginningDatetime` is in less than 48h. If the event is in less than 48 hours, then it cannot be cancelled
* `USED` The bookings has been used. → The booking has been validated by the venue and will be reimbursed in the next payment
* `CANCELLED` The bookings has been cancelled. → The booking has been cancelled by the beneficiary or by the provider
* `REIMBURSED` The bookings has been reimbursed. → The booking has been reimbursed by pass Culture to the venue


### Cancel a booking

#### For an event :
pass Culture’s beneficiary has 48h to cancel an event booking, unless the event `beginningDatetime` is in less than 48h. If the event is in less than 48 hours, then it cannot be cancelled

:::warning
Only bookings that have not been reimbursed can be modified.
:::

If you want to delete a booking :

* For an event :
    * You can delete the offer stock.
    * You can’t cancel an individual booking, but you can invalidate it (the booking). When the token is invalidated: the reservation reverts to the previous status. e.g.: if a booking is `USED`. You invalidate it, the booking will be `CONFIRMED`.
* For a product :
    * When the token is invalidated the reservation reverts to the previous status.
