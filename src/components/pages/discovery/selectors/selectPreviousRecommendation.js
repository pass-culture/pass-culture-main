import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import mapArgsToCacheKey from './mapArgsToCacheKey'
import selectCurrentRecommendation from './selectCurrentRecommendation'
import selectUniqAndIndexifiedRecommendations from './selectUniqAndIndexifiedRecommendations'

const selectPreviousRecommendation = createCachedSelector(
  selectUniqAndIndexifiedRecommendations,
  selectCurrentRecommendation,
  (recommendations, currentRecommendation) => {
    const previousRecommendation =
      currentRecommendation &&
      get(
        recommendations,
        recommendations.findIndex(
          recommendation => recommendation.id === currentRecommendation.id
        ) - 1
      )

    if (!previousRecommendation) {
      return undefined
    }

    // path
    const { mediationId, offerId } = previousRecommendation
    const path = `/decouverte/${offerId}/${mediationId || ''}`

    // return
    return Object.assign(
      {
        path,
      },
      previousRecommendation
    )
  }
)(mapArgsToCacheKey)

export default selectPreviousRecommendation
