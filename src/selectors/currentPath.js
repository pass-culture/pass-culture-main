import { createSelector } from 'reselect'

import { pathToCollection } from '../utils/translate'

export default createSelector(
  (state, ownProps) => ownProps.occasionType,
  (state, ownProps) => ownProps.occasionId,
  (occasionType, occasionId) => {
    let path = `occasions/${pathToCollection(occasionType)}`
    if (occasionId) {
      path = `${path}/${occasionId}`
    }
    return path
  }
)
