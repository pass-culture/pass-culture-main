import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, offerId) => offerId || ''

const selectOfferById = createCachedSelector(
  state => state.data.offers,
  (state, offerId) => offerId,
  (offers, offerId) => {
    if (offers) {
      return offers.find(offer => offer.id === offerId)
    }
  }
)(mapArgsToCacheKey)

export default selectOfferById
