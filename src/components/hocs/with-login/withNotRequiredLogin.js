import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withLogin from './withLogin'

export const handleSuccess = (currentUser, history, location) => {
  const redirect = getRedirectToCurrentLocationOrDiscovery({
    currentUser,
    ...location,
  })

  if (redirect) {
    history.push(redirect)
  }
}

export default withLogin({
  handleSuccess,
  isRequired: false,
})
