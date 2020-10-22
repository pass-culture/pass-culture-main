import createCachedSelector from 're-reselect'

export const selectOfferById = createCachedSelector(
  state => state.offers.list,
  (_state, offerId) => offerId,
  (offers, offerId) => {
    if (offers) {
      return offers.find(offer => offer.id === offerId)
    }
  }
)((_state, offerId = '') => offerId)

export const selectOffers = state => state.offers.list
