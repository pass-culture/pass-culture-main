import get from 'lodash.get'

const selectOffers = (onlineOnly, state) => {
  const offers = get(state, 'data.offers', [])
  return offers.filter(
    offer => offer.product.offerType.onlineOnly === onlineOnly
  )
}

export default selectOffers
