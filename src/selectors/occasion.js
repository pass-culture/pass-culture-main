import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'

const createSelectOccasion = () => createSelector(
  selectOccasions,
  (state, ownProps) => get(ownProps, 'match.params.occasionId'),
  (state, ownProps) => get(ownProps, 'occasion.id'),
  (occasions, paramsOccasionId, propsOccasionId) => {
    if (!occasions) {
      return
    }
    console.log('paramsOccasionId, propsOccasionId', paramsOccasionId, propsOccasionId, occasions)
    return occasions.find(o => o.id === (paramsOccasionId || propsOccasionId))
  }
)
export default createSelectOccasion

export const selectCurrentOccasion = createSelectOccasion()
