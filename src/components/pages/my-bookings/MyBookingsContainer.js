import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import MyBookings from './MyBookings'
import selectValidBookings from './selectors/selectValidBookings'
import { withRequiredLogin } from '../../hocs'
import { resetPageData } from '../../../reducers/data'
import { bookingNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => {
  const validBookings = selectValidBookings(state)
  return {
    validBookings,
  }
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
  resetPageData: () => dispatch(resetPageData()),
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MyBookings)
