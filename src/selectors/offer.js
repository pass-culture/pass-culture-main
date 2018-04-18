import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectUserMediation from './userMediation'

export function getOffer (userMediation, offerId) {
  return get(userMediation, 'userMediationOffers', [])
    .find(o => offerId ? (o.id === offerId) : true)
}

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  selectUserMediation,
  (pathname, userMediation) => {
    const [ , , offerId ] = pathname.split('/')
    return getOffer(userMediation, offerId)
  }
)
