import { compose } from 'redux'

import BookingsRecap from './BookingsRecap'
import { withRequiredLogin } from '../../hocs'

export default compose(withRequiredLogin)(BookingsRecap)
