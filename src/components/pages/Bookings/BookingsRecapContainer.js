import { compose } from 'redux'

import BookingsRecap from './BookingsRecap'
import { withRequiredLogin } from 'components/hocs'

export default compose(withRequiredLogin)(BookingsRecap)
