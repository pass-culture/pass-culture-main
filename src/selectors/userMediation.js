import { createSelector } from 'reselect'
import get from 'lodash.get';

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => state.data.userMediations || [],
  (pathname, userMediations) => {
    const [ , , offerId, mediationId ] = pathname.split('/')
    if (mediationId) {
      return userMediations.find(m => m.mediationId === mediationId)
    }
    return userMediations.find(m => get(m, 'userMediationOffers', [])
      .find(o => o.id === offerId))
  }
)
