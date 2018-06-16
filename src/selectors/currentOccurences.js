import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccurences from './occurences'

export default () => createSelector(
  selectOccurences,
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  (state, ownProps) => get(ownProps, 'occasion.id'),
  (occurences, venueId, occasionId) => {
    if (!occurences) {
      return
    }
    if (venueId) {
      return occurences.filter(o => o.venueId === venueId)
    }
  }
)
