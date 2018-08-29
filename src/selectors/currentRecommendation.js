// import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import recommendationsSelector from './recommendations'
// import { getHeaderColor } from '../utils/colors'
// import { filterAvailableDates } from '../helpers/filterAvailableDates'

const selectCurrentRecommendation = createCachedSelector(
  recommendationsSelector,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (allRecommendations, offerId, mediationId) => {
    const currentRecommendation = allRecommendations.find(recommendation => {
      const matchOffer = recommendation.offerId === offerId
      const matchMediation = recommendation.mediationId === mediationId
      return offerId === 'tuto' ? matchMediation : matchOffer
    })
    return currentRecommendation
  }
)(
  (state, offerId, mediationId, position) =>
    `${offerId || ''}/${mediationId || ''}/${position || ''}`
)

export default selectCurrentRecommendation
