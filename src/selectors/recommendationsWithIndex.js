import { createSelector } from 'reselect'
import selectUniqueRecommendations from './uniqueRecommendations'

export default createSelector(
  selectUniqueRecommendations,
  recommendations =>
    recommendations.map((reco, index) => Object.assign(reco, { index }))
)
