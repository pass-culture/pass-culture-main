import { createSelector } from 'reselect'

import selectOccurences from './occurences'
import selectSelectedVenueId from './selectedVenueId'

export default createSelector(
  selectOccurences,
  selectSelectedVenueId,
  (occurences, venueId) => {
    if (!occurences) {
      return
    }
    if (venueId) {
      return occurences.filter(o => o.venueId === venueId)
    }
  }
)
