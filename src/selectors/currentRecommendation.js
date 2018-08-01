import get from 'lodash.get'
import { createSelector } from 'reselect'

import recommendationsSelector from './recommendations'
import { getHeaderColor } from '../utils/colors'

export default createSelector(
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
      currentRecommendation = filteredRecommendations.find(r => r.offerId === offerId)
    }

    // undefined
    if (!currentRecommendation) {
      return undefined
    }

    // is finished
    // console.log('currentRecommendation', currentRecommendation)
    const isFinished = false
    /*
    const {}
    const offers = get(currentRecommendation, 'currentRecommendationOffers', [])
    const now = moment()
    return offers.every(o => moment(o.bookingLimitDatetime).isBefore(now))
    */
    // FIXME: also check that nbooking < available

    // colors
    const headerColor = getHeaderColor(currentRecommendation.firstThumbDominantColor)

    // return
    return Object.assign({
      isFinished,
      headerColor
    }, currentRecommendation)
  }
)
