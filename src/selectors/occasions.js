import createCachedSelector from 're-reselect';

import createVenuesSelector from './createVenues'

const venuesSelector = createVenuesSelector()

export default createCachedSelector(
  state => state.data.searchedOccasions || state.data.occasions,
  (state, offererId, venueId) => offererId ? venuesSelector(state, offererId) : [],
  (_, offererId, venueId) => venueId,
  (occasions, venues, venueId) => {
    const venueIds = [].concat(venueId || venues.map(v => v.id))

    return occasions.filter(o => venueIds.length ? venueIds.includes(o.venueId) : true)
  },
  (state, offererId, venueId) => `${offererId}/${venueId}`
)
