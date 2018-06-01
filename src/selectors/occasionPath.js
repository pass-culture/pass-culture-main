import { createSelector } from 'reselect'

import { pathToCollection } from '../utils/translate'

export default createSelector(
  (state, ownProps) => ownProps.match.params.occasionPath,
  (state, ownProps) => ownProps.match.params.occasionId,
  (occasionPath, occasionId) => {
    return `occasions/${pathToCollection(occasionPath)}/${occasionId !== 'nouveau' ? occasionId : ''}`
  }
)
