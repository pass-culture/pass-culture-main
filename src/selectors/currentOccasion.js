import { createSelector } from 'reselect'

import { collectionToPath } from '../utils/translate'

export default createSelector(
  state => state.data.occasions,
  (state, ownProps) => ownProps.match.params.occasionPath,
  (state, ownProps) => ownProps.match.params.occasionId,
  (occasions, occasionPath, occasionId) => {
    if (!occasions) { return }
    const currentOccasion = occasions.find(o =>
        occasionPath === collectionToPath(o.occasionType) &&
        o.id === occasionId
    )
    return currentOccasion
  }
)
