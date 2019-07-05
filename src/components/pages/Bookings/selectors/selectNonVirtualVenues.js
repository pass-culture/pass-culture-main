const selectNonVirtualVenues = state => {
  const venues = state.data.venues || []
  return venues.filter(venue => venue.isVirtual === false)
}

export default selectNonVirtualVenues
