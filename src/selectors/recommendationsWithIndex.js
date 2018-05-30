import { createSelector } from 'reselect'

import selectSortedRecommendations from './sortedRecommendations'

export default createSelector(
  selectSortedRecommendations,
  recommendations =>
    recommendations.map((reco, index) => Object.assign(reco, { index }))
)
