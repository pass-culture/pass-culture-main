import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'

export default createSelector(
  selectOccasions,
  (state, ownProps) => get(ownProps, 'match.params.occasionId'),
  (occasions, occasionId) => occasions &&
    occasions.find(o => o.id === occasionId)
)
