import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(
  selectCurrentRecommendation,
  recommendation =>
    recommendation &&
    recommendation.recommendationOffers &&
    recommendation.recommendationOffers.length === 0
)
