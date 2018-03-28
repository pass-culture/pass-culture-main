import { createSelector } from 'reselect'
import get from 'lodash.get';

export function getUserMediation (offerId, mediationId, userMediations) {
  if (mediationId) {
    return userMediations.find(m => m.mediationId === mediationId)
  }
  return userMediations.find(m => get(m, 'userMediationOffers', [])
    .find(o => o.id === offerId))
}

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => state.data.userMediations || [],
  (pathname, userMediations) => {
    const [ , , offerId, mediationId ] = pathname.split('/')
    return getUserMediation (offerId, mediationId, userMediations)
  }
)
