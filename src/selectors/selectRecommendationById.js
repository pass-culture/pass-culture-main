import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, recommendationId) {
  return recommendationId || ''
}

export const selectRecommendationById = createCachedSelector(
  state => state.data.recommendations,
  (state, recommendationId) => recommendationId,
  (recommendations, recommendationId) =>
    recommendations.find(recommendation => recommendation.id === recommendationId)
)(mapArgsToCacheKey)

export default selectRecommendationById
