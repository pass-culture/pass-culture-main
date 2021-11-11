import { getRedirectionPath } from './helpers'
import withLogin from './withLogin'

export const handleFail = (history, location) => {
  const { pathname, search } = location

  const fromUrl = encodeURIComponent(`${pathname}${search}`)

  history.push(`/connexion?de=${fromUrl}`)
}

export const handleSuccess = ({ currentUser, history, isHomepageDisabled, location }) => {
  const redirect = getRedirectionPath({
    currentUser,
    isHomepageDisabled,
    ...location,
  })

  if (redirect) {
    history.push(redirect)
  }
}

export default withLogin({
  handleFail,
  handleSuccess,
  isRequired: true,
})
