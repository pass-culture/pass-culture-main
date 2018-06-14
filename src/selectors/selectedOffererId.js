import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOffererOptions from './offererOptions'
import selectEventOccurences from './eventOccurences'

export default createSelector(
  selectOffererOptions,
  selectEventOccurences,
  (offererOptions, eventOccurences) =>
    get(offererOptions, '0.value') ||
    get(eventOccurences, '0.venue.managingOffererId')
)
