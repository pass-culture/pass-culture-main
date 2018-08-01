import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentRecommendation from './currentRecommendation'

export default createSelector(
  selectCurrentRecommendation,
  recommendation => get(recommendation, 'offer')
)
