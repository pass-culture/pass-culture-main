import { connect } from 'react-redux'
import { compose } from 'redux'

import BookingsRouter from './BookingsRouter'
import selectIsFeatureActive from '../../../selectors/data/selectIsFeatureActive'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export const mapStateToProps = state => {
  const isBookingsV2Active = selectIsFeatureActive(state, 'BOOKINGS_V2')

  return {
    isBookingsV2Active,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(BookingsRouter)
