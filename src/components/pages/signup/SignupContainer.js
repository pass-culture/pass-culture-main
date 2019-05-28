import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../../hocs'

import Signup from './Signup'

export default withRedirectToDiscoveryWhenAlreadyAuthenticated(Signup)
