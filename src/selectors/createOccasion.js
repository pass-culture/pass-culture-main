import { createSelector } from 'reselect'

import createOccasionsSelector from './createOccasions'

export default () => createSelector(
  createOccasionsSelector(),
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    if (!occasionId)
      return occasions

    return occasions.find(o => o.id === occasionId)
  }
)
