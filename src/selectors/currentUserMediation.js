import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectUserMediationsWithIndex from './userMediationsWithIndex'
import getUserMediation from '../getters/userMediation'

export default createSelector(
  state => state.router.location.pathname,
  selectUserMediationsWithIndex,
  (pathname, userMediations) => {
    const [, , offerId, mediationId] = pathname.split('/')
    let filteredUserMediations
    // NORMALY mediationId is ENOUGH TO FIND THE MATCHING
    // USER MEDIATION (BECAUSE WE PROPOSE ONLY ONE OFFER PER MEDIATION)
    // BUT TO BE SURE WE GET ALL THE AVAILABLES
    // (IF AT ANY CASE BACKEND ALGO SENT BACK DOUBLONS...BECAUSE OF SOME MISTAKES)
    if (mediationId) {
      filteredUserMediations = userMediations.filter(
        m => m.mediationId === mediationId
      )
    } else {
      filteredUserMediations = userMediations
    }
    // THEN DESAMBIGUATE WITH OFFER ID
    let userMediation
    if (offerId === 'tuto') {
      userMediation = filteredUserMediations[0]
    } else {
      userMediation = filteredUserMediations.find(m =>
        get(m, 'userMediationOffers', []).find(o => o.id === offerId)
      )
    }
    const hydratedUserMediation = getUserMediation({
      offerId,
      userMediation,
      userMediations,
    })
    return hydratedUserMediation
  }
)
