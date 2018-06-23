import get from 'lodash.get'
import { createSelector } from 'reselect'

import { selectCurrentOccasion } from './occasion'
import { selectVenues } from './venues'

const createSelectVenue = selectOccasion => createSelector(
  selectVenues,
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  selectOccasion,
  (venues, venueId, occasion) => {
    if (!venues) {
      return
    }
    console.log('OCCasion', occasion)
    return venues.find(v =>
      v.id === (venueId || get(occasion, 'venueId')))
  }
)
export default createSelectVenue

export const selectCurrentVenue = createSelectVenue(selectCurrentOccasion)
