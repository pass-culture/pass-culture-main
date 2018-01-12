export const getSellerFavoritesOptimistState = (state, action) => {
  let sellersFavorites
  const offers = state.offers.map(offer => {
    if (offer.id === id) {
      /*
      offer.sellersFavorites = action.config.body.concat(
        offer.sellersFavorites)
      */
      sellersFavorites = action.config.body.concat(
        offer.sellersFavorites)
    }
    return offer
  })
  return {
    // offers,
    sellersFavorites
  }
}
