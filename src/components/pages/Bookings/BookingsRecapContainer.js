import { compose } from 'redux'

import { withRequiredLogin } from 'components/hocs'

import BookingsRecap from './BookingsRecap'

export default compose(withRequiredLogin)(BookingsRecap)
