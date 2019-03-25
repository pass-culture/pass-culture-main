import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../../hocs/with-login'
import ActivationRoutes from './ActivationRoutes'

export default compose(
  withRedirectToDiscoveryWhenAlreadyAuthenticated,
  connect()
)(ActivationRoutes)
