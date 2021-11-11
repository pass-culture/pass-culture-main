/*
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { compose } from 'redux'

import { withTracking } from 'components/hocs'
import * as pcapi from 'repository/pcapi/pcapi'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Desk from './Desk'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export const mapDispatchToProps = dispatch => ({
  getBooking: code =>
    pcapi.getBooking(code).then(booking => {
      dispatch({
        type: 'GET_DESK_BOOKINGS',
        payload: booking,
      })

      return booking
    }),
  validateBooking: code => pcapi.validateBooking(code),
  invalidateBooking: code => pcapi.invalidateBooking(code),
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => ({
  ...stateProps,
  ...dispatchProps,
  trackValidateBookingSuccess: code => {
    ownProps.tracking.trackEvent({ action: 'validateBooking', name: code })
  },
})

export default compose(
  withTracking('Desk'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(Desk)
