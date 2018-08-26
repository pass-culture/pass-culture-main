import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import recommendationsSelector from './recommendations'
import { getHeaderColor } from '../utils/colors'
import { filterAvailableDates } from '../helpers/filterAvailableDates'

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
    const tz = get(currentRecommendation, 'tz')
    const stocks = get(currentRecommendation, 'offer.stocks')
    const availableDates = filterAvailableDates(stocks, tz)
    const isFinished = !(availableDates && availableDates.length > 0)

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
