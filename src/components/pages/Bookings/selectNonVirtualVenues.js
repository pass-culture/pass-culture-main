import get from "lodash.get";

const selectNonVirtualVenues = state => {
  const venues = get(state, 'data.venues', [])
  return venues.filter(venue => venue.isVirtual === false)
}

export default selectNonVirtualVenues
