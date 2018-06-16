import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedVenues from './selectedVenues'

export default (selectOccurences) => createSelector(
  selectSelectedVenues,
  selectOccurences,
  (venues, occurences) =>
    (venues && venues.length === 1 && venues[0].id) ||
    get(occurences, '0.venue.id')
)
