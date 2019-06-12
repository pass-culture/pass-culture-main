import { createSelector } from 'reselect'

export const selectDigitalOffers = createSelector(
  state => state.data.offers,
  offers => offers.find(offer => offer.product.offerType.onlineOnly === true)
)

export default selectDigitalOffers
