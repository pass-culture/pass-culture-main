import {connect} from 'react-redux'
import {compose} from 'redux'

import Bookings from '../Bookings-v2/Bookings'
import {withRequiredLogin} from '../../hocs'
import {requestData} from "redux-saga-data"

export const mapStateToProps = state => {
  const {data} = state
  const {bookingsRecap} = data
  return {bookingsRecap}
}

export const mapDispatchToProps = dispatch => ({
  requestGetAllBookingsRecap: (handleSuccess, handleFail) => dispatch(
    requestData({
      apiPath: '/bookings/pro',
      handleSuccess: handleSuccess,
      handleFail: handleFail,
    }),
  ),
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps, mapDispatchToProps),
)(Bookings)
