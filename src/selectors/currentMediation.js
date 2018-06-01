import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOccasion from './currentOccasion'

export default createSelector(
  selectCurrentOccasion,
  (state, ownProps) => ownProps.match.params.mediationId,
  (occasion, mediationId) => {
    if (mediationId === 'nouveau') return {}
    return get(occasion, 'mediations', []).find(m => m.id === mediationId)
  }
)
