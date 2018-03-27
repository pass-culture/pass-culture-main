import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => selectCurrentUserMediation(state),
  (currentUserMediation) => get(currentUserMediation, 'mediation')
)
