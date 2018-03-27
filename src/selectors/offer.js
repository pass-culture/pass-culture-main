import { createSelector } from 'reselect'
import get from 'lodash.get';

import selectUserMediation from './userMediation'

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  state => selectUserMediation(state),
  (pathname, userMediation) => {
    const [ , , offerId ] = pathname.split('/')
    console.log('offerId', offerId, userMediation)
    return get(userMediation, 'userMediationOffers', [])
      .find(o => o.id === offerId)
  }
)
