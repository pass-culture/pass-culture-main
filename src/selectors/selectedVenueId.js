import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectEventOccurences from './eventOccurences'
import selectSelectedVenues from './selectedVenues'

export default createSelector(
  selectSelectedVenues,
  selectEventOccurences,
  (venues, eventOccurences) =>
    (venues && venues.length === 1 && venues[0].id) ||
    get(eventOccurences, '0.venue.id')
)
