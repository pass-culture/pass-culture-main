import { createSelector } from 'reselect'

import { pathToCollection } from '../utils/translate'

export default createSelector(
  state => state.data.occasions,
  (state, ownProps) => ownProps.match.params.occasionPath,
  (state, ownProps) => ownProps.match.params.occasionId,
  (occasions, occasionPath, occasionId) => {
    return (occasions || []).find(o =>
      (
        // TODO: add filter on occastionType when available
        // in case object and event can have same id
        // o.occasionType === pathToCollection(occasionPath) &&
        o.id === occasionId))
  }
)
