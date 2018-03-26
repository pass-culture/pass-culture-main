import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => window.location.pathname.split('/').slice(-1).pop(), // TODO: get data from redux state
  state => selectCurrentUserMediation(state),
  (offerId, currentUserMediation) => {
    return get(currentUserMediation, 'userMediationOffers', []).find(o => o.id === offerId)
  }
)
