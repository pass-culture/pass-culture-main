import Desk from './Desk'
import { compose } from 'redux'
import { connect } from 'react-redux'

import { withRequiredLogin } from '../../hocs'
import { requestData } from "redux-saga-data"

export const mapDispatchToProps = (dispatch) => {
  return {
    getBookingFromCode: (code, handleSuccess, handleFail) => {
        dispatch(
          requestData({
            apiPath: `/bookings/token/${code}`,
            handleSuccess: handleSuccess,
            handleFail: handleFail,
            stateKey: 'deskBookings',
            method: 'GET'
          })
        )
      },
    validateBooking: (code, handleSuccess, handleFail) => {
      dispatch(
        requestData({
          apiPath: `/bookings/token/${code}`,
          handleFail: handleFail,
          handleSuccess: handleSuccess,
          method: 'PATCH',
        })
      )
    }
  }
}

export default compose(
  withRequiredLogin,
  connect(null, mapDispatchToProps)
)(Desk)
