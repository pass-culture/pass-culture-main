import get from 'lodash.get'
import { createSelector } from 'reselect'

import recommendationsSelector from './recommendations'

export default createSelector(
  recommendationsSelector,
  (state, offerId) => offerId,
  (state, offerId, mediationId) => mediationId,
  (recommendations, offerId, mediationId) => {
    let filteredRecommendations

    // prefilter by mediation
    if (mediationId) {
      filteredRecommendations = recommendations.filter(
        m => m.mediationId === mediationId
      )
    } else {
      filteredRecommendations = recommendations
    }

    // special tuto case
    let recommendation
    if (offerId === 'tuto') {
      recommendation = get(filteredRecommendations, '0')
    } else {
      recommendation = filteredRecommendations.find(r => r.offerId === offerId)
    }

    // undefined
    if (!recommendation) {
      return undefined
    }

    // is finished
    // console.log('recommendation', recommendation)
    /*
    const {}
    const offers = get(recommendation, 'recommendationOffers', [])
    const now = moment()
    return offers.every(o => moment(o.bookingLimitDatetime).isBefore(now))
    */
    // FIXME: also check that nbooking < available

    return recommendation
  }
)
