import { compose } from 'redux'

import BookingsRecap from '../Bookings-v2/BookingsRecap'
import { withRequiredLogin } from '../../hocs'

export default compose(withRequiredLogin)(BookingsRecap)
