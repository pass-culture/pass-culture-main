import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentRecommendationSelector from './currentRecommendation'
import recommendationsSelector from './recommendations'
import { getHeaderColor } from '../utils/colors'

export default createSelector(
  recommendationsSelector,
  currentRecommendationSelector,
  (recommendations, currentRecommendation) => {
    const nextRecommendation = currentRecommendation &&
      get(recommendations, recommendations.findIndex(recommendation =>
        recommendation.id === currentRecommendation.id) + 1)

    if (!nextRecommendation) {
      return undefined
    }

    const { mediationId, offerId } = nextRecommendation

    // path
    const path = `/decouverte/${offerId}/${mediationId || ''}`

    // headerColor
    const headerColor = getHeaderColor(currentRecommendation.firstThumbDominantColor)

    // return
    return Object.assign({
      headerColor,
      path
    }, nextRecommendation)
  }
)
