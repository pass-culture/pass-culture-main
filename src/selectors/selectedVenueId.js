import get from 'lodash.get'
import { createSelector } from 'reselect'

import createVenueSelector from './venues'

export default createSelector(
  createVenueSelector,
  (state, ownProps) => get(ownProps, 'occasion.venueId'),
  (venues, venueId) =>
    venueId ||
    (get(venues, 'length') === 1 && get(venues, '0.id'))
)
