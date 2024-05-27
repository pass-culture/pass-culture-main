---
sidebar_position: 2
---

# Individual offers

## `Products` & `Events`

**Indivual offers** are offers **maint for individual teenager**. They are split in two main categories:

- **📚 `Products`:** they can be either physical (_for instance a book or or a CD_) or digital (_for instance a subscription to a music streaming service_). **To manage those offers you will be mainly using the [product offers endpoints](/rest-api/#tag/Product-offer)**.
- **🎭 `Events`:** they can be either physical (_for instance a concert or a theater performance_) or digital (_for instance a online paiting lesson_). **To manage those offers you will be mainly using the [event offers endpoints](/rest-api/#tag/Event-offer)**.

## `Bookings`

**`Event` and `product` offers** share a common resource which is the **`booking` resource** :
- **For a product**, the **`booking`** is a **🪙 countermark**. This **countermark** will be used by the teenager either:
  - **in the case of a physical product**, to retrieve its order in the offerer shop. _For instance, if you are developping a stock management systems for bookshops, the seller will validate the teenager order by inputing the countermark in your software. Your software will then make a call to our [booking validation endpoint](/rest-api/#tag/Booking/operation/ValidateBookingByToken)_)
  - **in the case of a digital product**, to retrieve its order on the offerer website. _For instance, if you are a music streaming service, the teenager will validate its order by inputing the countermark in one of the field of the offer webiste form_.
- **For a event**, the **`booking`** is a **📅 reservation** for the event. **It can be linked to a ticket** if you plugged your ticketing solution to the Pass Culture application ; or **it can be a countermark**, if you chose to make the teenagers retrieve their tickets at the event venue.

To manage (list/validate/cancel) the booking through the API, you will be using the **[booking endpoints](/rest-api/#tag/Booking)**.

# Collective offers

**Collectives offers** are **events maint for scholar groupes**. They can be managed using the **[collective offers endpoints](/rest-api)**.
