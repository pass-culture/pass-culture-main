import get from 'lodash.get'
import { createSelector } from 'reselect'

import createOccasionsSelect from './createOccasions'

const createOccasionSelect = () => createSelector(
  createOccasionsSelect(),
  (state, occasionId) => occasionId,
  (occasions, occasionId) => {
    if (!occasionId)
      return occasions

    return occasions.find(o => o.id === occasionId)
  }
)
export default createOccasionSelect
