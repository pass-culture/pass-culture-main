import { createSelector } from 'reselect'

import isCurrentTutoSelector from './isCurrentTuto'
import currentMediationSelector from './currentMediation'
import currentRecommendationSelector from './currentRecommendation'

export default createSelector(
  currentRecommendationSelector,
  isCurrentTutoSelector,
  currentMediationSelector,
  (currentRecommendation, isCurrentTuto, currentMediation) =>
    !currentRecommendation ||
    (isCurrentTuto && currentMediation.thumbCount === 1)
)
