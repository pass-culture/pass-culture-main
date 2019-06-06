import withLogin from './withLogin'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'

const withRedirectToDiscoveryOrTypeformAfterLogin = withLogin({
  isRequired: false,
  successRedirect: getRedirectToCurrentLocationOrDiscovery,
})

export default withRedirectToDiscoveryOrTypeformAfterLogin
