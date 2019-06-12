import withLogin from './withLogin'

import { getRedirectToCurrentLocationOrTypeform } from './helpers'

const withRedirectToSigninOrTypeformAfterLogin = withLogin({
  failRedirect: ({ location }) => {
    const { pathname, search } = location
    const fromUrl = encodeURIComponent(`${pathname}${search}`)
    return `/connexion?de=${fromUrl}`
  },
  isRequired: true,
  successRedirect: getRedirectToCurrentLocationOrTypeform,
})

export default withRedirectToSigninOrTypeformAfterLogin
