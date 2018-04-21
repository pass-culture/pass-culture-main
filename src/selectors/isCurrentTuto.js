import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(
  selectCurrentRecommendation,
  recommendation =>
    recommendation &&
    recommendation.userMediationOffers &&
    recommendation.userMediationOffers.length === 0
)
