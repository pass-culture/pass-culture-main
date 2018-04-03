import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export function getMediation (userMediation) {
  return get(userMediation, 'mediation')
}

export default createSelector(
  selectUserMediation,
  getMediation
)
