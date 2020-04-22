import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from '../Bookings-v2/Bookings'
import { mapStateToProps } from '../Bookings-v2/BookingsContainer'
import { withRequiredLogin } from '../../hocs'


export default compose(
  withRequiredLogin,
  connect(null)
)(Bookings)
