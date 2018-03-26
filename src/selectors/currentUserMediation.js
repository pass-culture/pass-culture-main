import { createSelector } from 'reselect'
import get from 'lodash.get';

export default createSelector(
  state => window.location.pathname.split('/').slice(-1).pop(), // TODO: get data from redux state
  state => state.data.userMediations || [],
  (offerId, mediations) => {
    return mediations.find(m => get(m, 'userMediationOffers', []).find(o => o.id === offerId))
  }
)
