const selectOffers = (state, isDigial) => {
  const offers = state.data.offers || []
  return offers.filter(offer => offer.isDigital === isDigial)
}

export default selectOffers
