import get from "lodash.get";

const selectOffersByVenueId = (venueId, state) => {
  const offers = get(state, 'data.offers', [])
  return offers.filter(offer => offer.venueId === venueId)
}

export default selectOffersByVenueId
