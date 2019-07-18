const selectOffersByVenueId = (state, venueId) => {
  let offers = []
  if (state.data) {
    offers = state.data.offers || []
  }
  return offers.filter(offer => offer.venueId === venueId)
}

export default selectOffersByVenueId
