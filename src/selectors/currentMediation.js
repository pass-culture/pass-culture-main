import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'
// import getMediation from '../getters/mediation'

export default createSelector(
  currentRecommendationSelector,
  currentRecommendation => get(currentRecommendation, 'mediation')
)
