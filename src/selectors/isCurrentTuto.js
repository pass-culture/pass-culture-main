import { createSelector } from 'reselect'

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  selectCurrentUserMediation,
  userMediation =>
    userMediation
    && userMediation.userMediationOffers
    && userMediation.userMediationOffers.length === 0
)
