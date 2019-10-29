import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import MyBookings from './MyBookings'
import { selectBookings } from '../../../selectors/data/bookingsSelector'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import { myBookingsNormalizer } from '../../../utils/normalizers'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'

export const mapStateToProps = state => {
  const isQrCodeFeatureDisabled = selectIsFeatureDisabled(state, 'QR_CODE')
  return {
    bookings: selectBookings(state),
    isQrCodeFeatureDisabled,
  }
}

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
