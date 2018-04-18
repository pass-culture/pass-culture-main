import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export default createSelector(
  selectUserMediation,
  userMediation =>
    userMediation
    && userMediation.userMediationOffers.length === 0
)
