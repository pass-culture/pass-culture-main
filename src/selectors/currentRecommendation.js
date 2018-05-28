import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectRecommendationQuery from './recommendationQuery'
import selectRecommendationsWithIndex from './recommendationsWithIndex'
import getRecommendation from '../getters/recommendation'

export default createSelector(
  state => state.router.location.pathname,
  selectRecommendationsWithIndex,
  selectRecommendationQuery,
  (
    pathname,
    recommendations,
    recommendationQuery
  ) => {

    // NOTE: you will see that recommendationQuery is not actually
    // used in the body of this function, but it is still necessary
    // to trigger this selector again when /recommendations/<recommendationId>
    // requests has been called
    // (as the state.data.recommendations is not mutated through these kinds of calls)

    const [, , offerId, mediationId] = pathname.split('/')
    let filteredRecommendations
    // NORMALY mediationId is ENOUGH TO FIND THE MATCHING
    // USER MEDIATION (BECAUSE WE PROPOSE ONLY ONE OFFER PER MEDIATION)
    // BUT TO BE SURE WE GET ALL THE AVAILABLES
    // (IF AT ANY CASE BACKEND ALGO SENT BACK DOUBLONS...BECAUSE OF SOME MISTAKES)
    if (mediationId) {
      filteredRecommendations = recommendations.filter(
        m => m.mediationId === mediationId
      )
    } else {
      filteredRecommendations = recommendations
    }
    // THEN DESAMBIGUATE WITH OFFER ID
    let recommendation
    if (offerId === 'tuto') {
      recommendation = filteredRecommendations[0]
    } else {
      recommendation = filteredRecommendations.find(m =>
        get(m, 'recommendationOffers', []).find(o => o.id === offerId)
      )
    }
    const hydratedRecommendation = getRecommendation({
      offerId,
      recommendation,
      recommendations,
    })
    return hydratedRecommendation
  }
)
