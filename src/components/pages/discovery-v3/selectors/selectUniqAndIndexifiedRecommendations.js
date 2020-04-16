import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

const selectUniqAndIndexifiedRecommendations = createSelector(
  state => state.data.recommendations,
  recommendations => {
    let filteredRecommendations = recommendations.filter(
      recommendation => recommendation.productOrTutoIdentifier
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.productOrTutoIdentifier
    )

    filteredRecommendations = filteredRecommendations.map((recommendation, index) =>
      Object.assign({ index }, recommendation)
    )

    return filteredRecommendations
  }
)

export default selectUniqAndIndexifiedRecommendations
