import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOccasion from './currentOccasion'

export default createSelector(
  selectCurrentOccasion,
  (state, ownProps) => ownProps.match.params.mediationId,
  state => state.data.mediations,
  (occasion, mediationId, mediations) => {
    if (mediations && mediations.length === 1) {
      return mediations[0]
    }
    return get(occasion, 'mediations', [])
      .find(m => m.id === mediationId)
  }
)
