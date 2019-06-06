import withLogin from './withLogin'

import { getRedirectToDiscoveryOrTypeform } from './helpers'

const withRedirectToDiscoveryOrTypeformAfterLogin = withLogin({
  isRequired: false,
  successRedirect: getRedirectToDiscoveryOrTypeform,
})

export default withRedirectToDiscoveryOrTypeformAfterLogin
