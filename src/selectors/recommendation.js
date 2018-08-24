import createCachedSelector from 're-reselect'

import recommendationsSelector from './recommendations'

export const selectRecommendation = createCachedSelector(
  state => recommendationsSelector(state),
  (state, recommendationId) => recommendationId,
  (recommendations, recommendationId) =>
    recommendations.find(
      recommendation => recommendation.id === recommendationId
    )
)((state, recommendationId) => recommendationId || '')

export default selectRecommendation
