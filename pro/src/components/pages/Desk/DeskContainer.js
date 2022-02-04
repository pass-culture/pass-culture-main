import { connect } from 'react-redux'
import { compose } from 'redux'

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

export default compose(connect(mapStateToProps, mapDispatchToProps))(Desk)
