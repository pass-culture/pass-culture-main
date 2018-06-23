import get from 'lodash.get'
import { createSelector } from 'reselect'

import { selectVenues } from './venues'

export default createSelector(
  selectVenues,
  (state, ownProps) => get(ownProps, 'occasion.venueId'),
  (venues, venueId) =>
    venueId ||
    (get(venues, 'length') === 1 && get(venues, '0.id'))
)
