import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export function getMediation (userMediation) {
  return userMediation.mediation
}

export default createSelector(
  state => selectUserMediation(state),
  getMediation
)
