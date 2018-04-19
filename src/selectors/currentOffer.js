import { createSelector } from 'reselect'

import selectCurrentUserMediation from './currentUserMediation'
import getOffer from '../getters/offer'

export default createSelector(
  state => state.router.location.pathname, // TODO: get data from redux state
  selectCurrentUserMediation,
  (pathname, userMediation) => {
    const [ , , offerId ] = pathname.split('/')
    return getOffer(userMediation, offerId)
  }
)
