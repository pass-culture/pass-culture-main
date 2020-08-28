import { connect } from 'react-redux'
import { compose } from 'redux'

import { selectBookings } from '../../../redux/selectors/data/bookingsSelectors'
import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import { myBookingsNormalizer } from '../../../utils/normalizers'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import MyBookings from './MyBookings'

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
