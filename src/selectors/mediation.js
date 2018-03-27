import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export function getMediation (userMediation) {
  return userMediation.mediation
}

export default createSelector(
  selectUserMediation,
  getMediation
)
