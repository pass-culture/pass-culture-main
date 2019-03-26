import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../../hocs/with-login'
import ActivationRoutes from './ActivationRoutes'

export default withRedirectToDiscoveryWhenAlreadyAuthenticated(ActivationRoutes)
