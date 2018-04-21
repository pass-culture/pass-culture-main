import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentUserMediation from './currentUserMediation'

export default createSelector(
  state => state.data.bookings,
  selectCurrentUserMediation,
  (bookings, userMediation) => {
    return []
      .concat(bookings)
      .find(b => get(b, 'userMediationId') === get(userMediation, 'id'))
  }
)
