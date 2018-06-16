import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOffererOptions from './offererOptions'

export default (selectOccurences) => createSelector(
  selectOffererOptions,
  selectOccurences,
  (offererOptions, occurences) =>
    get(offererOptions, '0.value') ||
    get(occurences, '0.venue.managingOffererId')
)
