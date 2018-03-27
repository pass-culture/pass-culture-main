import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => selectCurrentUserMediation(state),
  (pathname, currentUserMediation) => {
    const [ , , offerId ] = pathname.split('/')
    console.log('offerId', offerId, currentUserMediation)
    return get(currentUserMediation, 'userMediationOffers', [])
      .find(o => o.id === offerId)
  }
)
