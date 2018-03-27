import { createSelector } from 'reselect'
import selectCurrentUserMediation from './currentUserMediation'
import get from 'lodash.get';

export default createSelector(
  state => state.data.bookings,
  state => selectCurrentUserMediation(state),
  (bookings, currentUserMediation) => {
    return [].concat(bookings).find(b =>
      (get(b, 'userMediationId') === get(currentUserMediation, 'id')))
  }
)
