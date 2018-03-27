import { createSelector } from 'reselect'
import get from 'lodash.get';

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => state.data.userMediations || [],
  (pathname, userMediations) => {
    const [ , , offerId, userMediationId ] = pathname.split('/')
    if (userMediationId) {
      return userMediations.find(m => m.id === userMediationId)
    }
    return userMediations.find(m => get(m, 'userMediationOffers', []).find(o => o.id === offerId))
  }
)
