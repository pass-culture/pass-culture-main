import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedVenues from './selectedVenues'

export default createSelector(
  selectSelectedVenues,
  (state, ownProps) => get(ownProps, 'occasion.venueId'),
  (venues, venueId) =>
    venueId ||
    (venues && venues.length === 1 && venues[0].id)
)
