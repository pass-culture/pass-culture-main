import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectUserMediation from './userMediation'

export function getOffer (offerId, userMediation) {
  return get(userMediation, 'userMediationOffers', [])
    .find(o => o.id === offerId)
}

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => selectUserMediation(state),
  (pathname, userMediation) => {
    const [ , , offerId ] = pathname.split('/')
    return getOffer(offerId, userMediation)
  }
)
