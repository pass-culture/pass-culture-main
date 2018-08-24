import get from 'lodash.get'
import moment from 'moment'
import createCachedSelector from 're-reselect'

import recommendationsSelector from './recommendations'
import { getHeaderColor } from '../utils/colors'

const hasStockAvailables = recommendations => {
  const now = moment()
  const stocks = get(recommendations, 'offer.stocks')
  // tuto n'a pas de stock
  const filtered = (stocks || []).filter(item => {
    const date = item.bookingLimitDatetime
    return now.isSameOrAfter(date)
  })
  return filtered && filtered.length > 0
}

const selectCurrentRecommendation = createCachedSelector(
  recommendationsSelector,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (currentRecommendations, offerId, mediationId) => {
    let filteredRecommendations

    // prefilter by mediation
    if (mediationId) {
      filteredRecommendations = currentRecommendations.filter(
        m => m.mediationId === mediationId
      )
    } else {
      filteredRecommendations = currentRecommendations
    }

    // special tuto case
    let currentRecommendation
    if (offerId === 'tuto') {
      currentRecommendation = get(filteredRecommendations, '0')
    } else {
      currentRecommendation = filteredRecommendations.find(
        r => r.offerId === offerId
      )
    }

    // undefined
    if (!currentRecommendation) {
      return undefined
    }

    // is finished
    const isFinished = !hasStockAvailables(currentRecommendation)

    // colors
    const headerColor = getHeaderColor(
      currentRecommendation.firstThumbDominantColor
    )

    // return
    return Object.assign(
      {
        headerColor,
        isFinished,
      },
      currentRecommendation
    )
  }
)(
  (state, offerId, mediationId, position) =>
    `${offerId || ''}/${mediationId || ''}/${position || ''}`
)

export default selectCurrentRecommendation
