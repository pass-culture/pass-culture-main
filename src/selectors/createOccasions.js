import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

export default (selectVenues= createVenuesSelector()) => createSelector(
  state => state.data.searchedOccasions || state.data.occasions,
  (state, offererId, venueId) => offererId ? selectVenues(state, offererId) : [],
  (_, offererId, venueId) => venueId,
  (occasions, venues, venueId) => {
    const venueIds = [].concat(venueId || venues.map(v => v.id))

    return occasions.filter(o => venueIds.length ? venueIds.includes(o.venueId) : true)
  }
)
