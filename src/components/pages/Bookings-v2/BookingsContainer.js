import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from '../Bookings-v2/Bookings'
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
)(Bookings)
