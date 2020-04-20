import { createSelector } from 'reselect'

const selectUniqAndIndexifiedRecommendations = createSelector(
  state => state.data.recommendations,
  recommendations => {
    const filteredRecommendations = recommendations.map((recommendation, index) =>
      Object.assign({ index }, recommendation)
    )

    return filteredRecommendations
  }
)

export default selectUniqAndIndexifiedRecommendations
