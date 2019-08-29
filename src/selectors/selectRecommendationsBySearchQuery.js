import uniqBy from 'lodash.uniqby'

const selectRecommendationsBySearchQuery = (state, location) => {
  let filteredRecommendations = state.data.recommendations.filter(
    recommendation => recommendation.search === location.search
  )
  filteredRecommendations = uniqBy(
    filteredRecommendations,
    recommendation => recommendation.productOrTutoIdentifier
  )

  return filteredRecommendations
}

export default selectRecommendationsBySearchQuery
