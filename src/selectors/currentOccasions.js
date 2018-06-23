import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'

export default (selectOccurences) => createSelector(
  selectOccasions,
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  (occasions, occurences, venueId) =>
    occasions.filter(o => o.venueId === venueId)
  }
)
