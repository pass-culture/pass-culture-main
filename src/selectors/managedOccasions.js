import { createSelector } from 'reselect'

import selectOccasions from './occasions'

export default selectManagedVenues => createSelector(
  selectOccasions,
  selectManagedVenues,
  (occasions, venues) => {
    if (!venues) {
      return
    }
    const venueIds = venues.map(v => v.id)
    return occasions && occasions.filter(occasion => venueIds.includes(occasion.venueId))
  }
)
