const selectOffersByVenueId = (venueId, state) => {
  const { offers } = state.data || []
  return offers.filter(offer => offer.venueId === venueId)
}

export default selectOffersByVenueId
