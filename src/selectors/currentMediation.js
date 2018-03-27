import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  (state, ownProps) => selectCurrentUserMediation(state, ownProps),
  (currentUserMediation) => get(currentUserMediation, 'mediation')
)
