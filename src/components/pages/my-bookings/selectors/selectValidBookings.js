import { createSelector } from 'reselect'

export const getIsNotAnActivationOffer = offer => {
  const { type } = offer

  if (!type) return false

  const isActivationType = type === 'EventType.ACTIVATION' || type === 'ThingType.ACTIVATION'

  return !isActivationType
}

export const selectValidBookings = createSelector(
  state => state.data.bookings,
  state => state.data.offers,
  state => state.data.stocks,
  (bookings, offers, stocks) =>
    offers
      .filter(getIsNotAnActivationOffer)
      .map(offer =>
        bookings.find(booking => {
          const stock = stocks.find(stock => stock.id === booking.stockId)

          return stock.offerId === offer.id
        })
      )
      .filter(booking => booking !== undefined)
)

export default selectValidBookings
