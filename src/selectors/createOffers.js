import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.offers,
  (state, venueId) => venueId,
  (offers, venueId) => {
    if (venueId)
      offers = offers.filter(o => o.managedVenueIds.includes(venueId))
    return offers
  }
)
