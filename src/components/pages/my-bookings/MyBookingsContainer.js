import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import MyBookings from './MyBookings'
import { selectBookings } from '../../../selectors/data/bookingsSelector'
import { withRequiredLogin } from '../../hocs'
import { myBookingsNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = state => ({
  bookings: selectBookings(state),
})

export const mapDispatchToProps = dispatch => ({
  requestGetBookings: (handleFail, handleSuccess) => {
    dispatch(
      requestData({
        apiPath: '/bookings',
        handleFail,
        handleSuccess,
        normalizer: myBookingsNormalizer,
      })
    )
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MyBookings)
