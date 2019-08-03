import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import MyBookingsLists from './MyBookingsLists'
import selectOtherBookings from './selectors/selectOtherBookings'
import selectSoonBookings from './selectors/selectSoonBookings'
import { bookingNormalizer } from '../../../../utils/normalizers'

export const mapStateToProps = state => {
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, soonBookings }
}

export const mapDispatchToProps = dispatch => ({
  requestGetBookings: (handleFail, handleSuccess) => {
    dispatch(
      requestData({
        apiPath: '/bookings',
        handleFail,
        handleSuccess,
        normalizer: bookingNormalizer,
      })
    )
  },
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MyBookingsLists)
