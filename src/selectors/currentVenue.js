import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.venues,
  (state, ownProps) => ownProps.match.params.venueId,
  state => state.data.venueProviders,
  state => state.data.occasions,
  (venues, venueId, venueProviders, occasions) => {
    if (!venues) {
      return
    }
    const venue = venues.find(v => v.id === venueId)
    if (!venue) {
      return
    }

    const filteredVenueProviders = venueProviders &&
      venueProviders.filter(vp => vp.venueId === venueId)
    if (filteredVenueProviders) {
      filteredVenueProviders.forEach(vp => {
        vp.occasions = occasions && occasions.filter(occasion =>
          occasion.lastProviderId === vp.providerId)
      })
    }
    venue.venueProviders = filteredVenueProviders

    return venue
  }
)
