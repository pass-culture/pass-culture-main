import { createSelector } from 'reselect'

import selectIsCurrentTuto from './isCurrentTuto'
import selectCurrentMediation from './currentMediation'
import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(
  selectCurrentRecommendation,
  selectIsCurrentTuto,
  selectCurrentMediation,
  (currentRecommendation, isCurrentTuto, currentMediation) =>
    !currentRecommendation ||
    (isCurrentTuto && currentMediation.thumbCount === 1)
)
