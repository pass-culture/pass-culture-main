import { createSelector } from 'reselect'

import createVenuesSelector from './createVenues'

const selectVenues = createVenuesSelector()

export default () => createSelector(
  state => state.data.searchedOccasions || state.data.occasions,
  selectVenues,
  (_, offererId, venueId) => venueId,
  (occasions, venues, venueId) => {

    if (venues.length) {
      const venueIds = venues.map(v => v.id)
      occasions = occasions.filter(o => venueIds.includes(o.venueId))
    }

    // TODO: find the link between occasion and venue
    if (venueId)
      occasions = occasions.filter(o => o.venueId === venueId)

    return occasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
