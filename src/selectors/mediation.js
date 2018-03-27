import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectUserMediation from './userMediation'

export default createSelector(
  (state, ownProps) => selectUserMediation(state, ownProps),
  (userMediation) => get(userMediation, 'mediation')
)
