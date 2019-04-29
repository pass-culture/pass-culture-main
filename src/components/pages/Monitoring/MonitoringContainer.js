import { compose } from 'redux'

import Monitoring from './Monitoring'
import { withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'

export default compose(withRedirectToSigninWhenNotAuthenticated)(Monitoring)
