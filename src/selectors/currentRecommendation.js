import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import recommendationsSelector from './recommendations'
import { getHeaderColor } from '../utils/colors'

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
    const isFinished = false
    /*
    const {}
    const offers = get(currentRecommendation, 'currentRecommendationOffers', [])
    const now = moment()
    return offers.every(o => moment(o.bookingLimitDatetime).isBefore(now))
    */
    // FIXME: also check that nbooking < available

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
