import { createSelector } from 'reselect'
import get from 'lodash.get';

export function getUserMediation (offerId, mediationId, userMediations) {
  let filteredUserMediations
  // NORMALY mediationId is ENOUGH TO FIND THE MATCHING
  // USER MEDIATION (BECAUSE WE PROPOSE ONLY ONE OFFER PER MEDIATION)
  // BUT TO BE SURE WE GET ALL THE AVAILABLES
  // (IF AT ANY CASE BACKEND ALGO SENT BACK DOUBLONS...BECAUSE OF SOME MISTAKES)
  if (mediationId) {
    filteredUserMediations = userMediations.filter(m => m.mediationId === mediationId)
  } else {
    filteredUserMediations = userMediations
  }
  // THEN DESAMBIGUATE WITH OFFER ID
  if (offerId === 'tuto') {
    return filteredUserMediations[0]
  } else {
    return filteredUserMediations.find(m => get(m, 'userMediationOffers', [])
      .find(o => o.id === offerId))
  }
}

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => state.data.userMediations || [],
  (pathname, userMediations) => {
    const [ , , offerId, mediationId ] = pathname.split('/')
    return getUserMediation (offerId, mediationId, userMediations)
  }
)
