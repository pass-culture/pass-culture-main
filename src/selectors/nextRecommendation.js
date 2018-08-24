import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import currentRecommendationSelector from './currentRecommendation'
import recommendationsSelector from './recommendations'

const nextRecommendationSelector = createCachedSelector(
  recommendationsSelector,
  currentRecommendationSelector,
  (recommendations, currentRecommendation) => {
    const nextRecommendation =
      currentRecommendation &&
      get(
        recommendations,
        recommendations.findIndex(
          recommendation => recommendation.id === currentRecommendation.id
        ) + 1
      )

    if (!nextRecommendation) {
      return undefined
    }

    const { mediationId, offerId } = nextRecommendation

    // path
    const path = `/decouverte/${offerId}/${mediationId || ''}`

    // return
    return Object.assign(
      {
        path,
      },
      nextRecommendation
    )
  }
)(
  (state, offerId, mediationId, position) =>
    `${offerId || ''}/${mediationId || ''}/${position || ''}`
)

export default nextRecommendationSelector
