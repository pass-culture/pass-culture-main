import { createSelector } from 'reselect'

const selectIndexifiedRecommendations = createSelector(
  state => state.data.recommendations,
  recommendations => {
    return recommendations.map((recommendation, index) => Object.assign({ index }, recommendation))
  }
)

export default selectIndexifiedRecommendations
