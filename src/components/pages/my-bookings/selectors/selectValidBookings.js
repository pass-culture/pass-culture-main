import { createSelector } from 'reselect'

export const getIsNotAnActivationOffer = offer => {
  const { type: offerType } = offer
  if (!offerType) return false
  const isActivationType =
    offerType === 'EventType.ACTIVATION' || offerType === 'ThingType.ACTIVATION'
  return !isActivationType
}

export const selectValidBookings = createSelector(
  state => state.data.bookings,
  state => state.data.offers,
  (bookings, offers) =>
    offers
      .filter(getIsNotAnActivationOffer)
      .map(offer => bookings.find(booking => booking.stock.offerId === offer.id))
)

export default selectValidBookings
