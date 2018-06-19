import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedVenues from './selectedVenues'

export default createSelector(
  selectSelectedVenues,
  (state, ownProps) => get(ownProps, 'currentOccasion.venueId'),
  (venues, venueId) =>
    venueId ||
    (get(venues, 'length') === 1 && get(venues, '0.id'))
)
