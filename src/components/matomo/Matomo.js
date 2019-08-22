import PropTypes from 'prop-types'

const TEAM_DOMAIN_REGEX = /^[a-zA-Z0-9_.+-]+@(octo.com|passculture.app|btmx.fr)/g
const SANDBOX_DOMAIN_REGEX = /^[a-zA-Z0-9_.+-]+@(momarx.io|hlettre.com|youpi.com|violet.fr)/g

const getUserType = email => {
  if (email.match(SANDBOX_DOMAIN_REGEX)) {
    return 'SANDBOX USER'
  } else if (email.match(TEAM_DOMAIN_REGEX)) {
    return 'TECH or BIZ USER'
  } else {
    return 'PRO USER'
  }
}

const Matomo = ({ location, user }) => {
  const Matomo = window._paq || []

  Matomo.push(['setCustomUrl', location.pathname])
  Matomo.push(['setDocumentTitle', document.title])

  let userId = 'ANONYMOUS'

  if (user) {
    userId = getUserType(user.email)
  }

  Matomo.push(['setUserId', userId])

  if (!user) {
    Matomo.push(['resetUserId'])
  }

  Matomo.push(['trackPageView'])
  return null
}

Matomo.defaultProps = {
  user: {},
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
  user: PropTypes.shape(),
}

export default Matomo
