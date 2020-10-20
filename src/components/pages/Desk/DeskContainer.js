import { withRequiredLogin, withTracking } from 'components/hocs'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { fetchFromApiWithCredentials } from 'utils/fetch'
import Desk from './Desk'

export const mapDispatchToProps = dispatch => ({
  getBooking: code =>
    fetchFromApiWithCredentials(`/v2/bookings/token/${code}`).then(booking => {
      dispatch({
        type: 'GET_DESK_BOOKINGS',
        payload: booking,
      })

      return booking
    }),
  validateBooking: code => fetchFromApiWithCredentials(`/v2/bookings/use/token/${code}`, 'PATCH'),
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
  withRequiredLogin,
  connect(null, mapDispatchToProps, mergeProps)
)(Desk)
