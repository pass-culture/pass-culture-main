import { createSelector } from 'reselect'
import get from 'lodash.get';

export default createSelector(
  (state, ownProps) => ownProps && ownProps.id,
  state => state.router.location.pathname, // TODO: get data from redux state
  state => state.data.userMediations || [],
  (id, pathname, userMediations) => {
    if (id) {
      return userMediations.find(m => m.id === id)
    }
    const [ , , offerId, mediationId ] = pathname.split('/')
    if (mediationId) {
      return userMediations.find(m => m.mediationId === mediationId)
    }
    return userMediations.find(m => get(m, 'userMediationOffers', [])
      .find(o => o.id === offerId))
  }
)
