import { connect } from 'react-redux'
import { compose } from 'redux'

import BookingsRecap from '../Bookings-v2/BookingsRecap'
import { withRequiredLogin } from '../../hocs'
import { requestData } from 'redux-saga-data'

export const mapDispatchToProps = dispatch => ({
  requestGetAllBookingsRecap: handleSuccess =>
    dispatch(
      requestData({
        apiPath: '/bookings/pro',
        handleSuccess: handleSuccess,
      })
    ),
})

export default compose(
  withRequiredLogin,
  connect(
    null,
    mapDispatchToProps
  )
)(BookingsRecap)
