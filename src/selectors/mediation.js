import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOccasion from './occasion'

const createSelectMediation = () => createSelector(
  selectOccasion,
  (state, ownProps) => ownProps.match.params.mediationId,
  state => state.data.mediations,
  (currentOccasion, mediationId, mediations) => {
    if (mediations && mediations.length === 1) {
      return mediations[0]
    }
    return get(currentOccasion, 'mediations', [])
      .find(m => m.id === mediationId)
  }
)
export default createSelectMediation

export const selectCurrentMediation = createSelectMediation()
