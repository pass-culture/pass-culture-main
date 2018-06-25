import get from 'lodash.get'
import { createSelector } from 'reselect'

// import { selectCurrentOccasion } from './occasion'
import createSelectVenues from './venues'
import createSelectOccasion from './occasion'

const createSelectVenue = () => createSelector(
  createSelectVenues(),
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  createSelectOccasion(),
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

// Don't do that: exports are cached, so the method is called only once
// export const selectCurrentVenue = createSelectVenue(selectCurrentOccasion)
