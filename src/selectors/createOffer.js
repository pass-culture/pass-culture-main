import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.offers,
  (state, offerId) => offerId,
  (offers, offerId) => offers.find(offer => offer.id === offerId)
)
