import get from 'lodash.get'
import { createSelector } from 'reselect'

// import { selectCurrentOccasion } from './occasion'
import createVenuesSelect from './createVenues'
import createOccasionSelect from './createOccasion'

const createSelectVenue = () => createSelector(
  createVenuesSelect(),
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  createOccasionSelect(),
  (venues, venueId, occasion) => {
    if (!venues) {
      return
    }
    return venues.find(v =>
      v.id === (venueId || get(occasion, 'venueId')))
  }
)
export default createSelectVenue

// Don't do that: exports are cached, so the method is called only once
// export const selectCurrentVenue = createSelectVenue(selectCurrentOccasion)
