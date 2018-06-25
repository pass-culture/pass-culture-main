import get from 'lodash.get'
import { createSelector } from 'reselect'

import createOccasionsSelector from './createOccasions'

const createOccasionSelector = () => createSelector(
  createOccasionsSelector(),
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    if (!occasionId)
      return occasions

    return occasions.find(o => o.id === occasionId)
  }
)
export default createOccasionSelector
