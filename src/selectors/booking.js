import get from 'lodash.get';
import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export default createSelector(
  state => state.data.bookings,
  selectUserMediation,
  (bookings, userMediation) => {
    return [].concat(bookings).find(b =>
      (get(b, 'userMediationId') === get(userMediation, 'id')))
  }
)
