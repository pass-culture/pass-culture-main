import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasionQuery from './occasionQuery'

export default createSelector(
  state => state.data.occasions,
  (state, ownProps) => ownProps.occasionId,
  (occasions, occasionId, occasionQuery) =>
    occasions && occasions.find(o => o.id === occasionId)
)
