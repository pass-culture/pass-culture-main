import { compose } from 'redux'

import Bookings from './Bookings'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'

export default compose(withRedirectToSigninWhenNotAuthenticated)(Bookings)
