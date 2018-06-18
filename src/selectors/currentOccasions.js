import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'

export default (selectOccurences) => createSelector(
  selectOccasions,
  selectOccurences,
  (state, ownProps) => ownProps.match.params.venueId,
  (occasions, occurences, venueId) => {
    return occasions
      .filter(o => venueId
        ? o.occurences.some(occ => occ.venueId === venueId)
        : true
      )
  }
)
