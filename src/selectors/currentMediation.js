import { createSelector } from 'reselect'
import get from 'lodash.get'

import selectCurrentOccasion from './currentOccasion'
import { pathToCollection } from '../utils/translate'

export default createSelector(
  selectCurrentOccasion,
  (state, ownProps) => ownProps.match.params.mediationId,
  (occasion, mediationId) => {
    if (mediationId === 'nouveau') return {}
    return get(occasion, 'mediations', []).find(m => m.id === mediationId)
  }
)
