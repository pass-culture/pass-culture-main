import get from 'lodash.get'
import { createSelector } from 'reselect'

export default (selectCurrentOccurences) => createSelector(
  selectCurrentOccurences,
  (offererOptions, currentOccurences) =>
    get(currentOccurences, '0.venue.managingOffererId')
)
