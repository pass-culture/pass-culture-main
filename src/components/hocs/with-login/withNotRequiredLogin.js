import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withLogin from './withLogin'

export const handleSuccess = ({ currentUser, history, isHomepageDisabled, location }) => {
  const redirect = getRedirectToCurrentLocationOrDiscovery({
    currentUser,
    isHomepageDisabled,
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
