import { createSelector } from 'reselect'

import createOccasionsSelector from './createOccasions'

const occasionsSelector = createOccasionsSelector()

export default () => createSelector(
  (state) => occasionsSelector(state),
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    return occasions.find(o => o.id === occasionId)
  }
)
