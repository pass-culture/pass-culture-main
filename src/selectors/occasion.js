import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'

export default () => createSelector(
  selectOccasions,
  (state, ownProps) => get(ownProps, 'match.params.occasionId'),
  (state, ownProps) => get(ownProps, 'occasion.id'),
  (occasions, paramsOccasionId, propsOccasionId) => occasions &&
    occasions.find(o => o.id === (paramsOccasionId || propsOccasionId)
)
