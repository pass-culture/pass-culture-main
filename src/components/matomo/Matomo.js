import PropTypes from 'prop-types'
import queryString from 'query-string'

const TEAM_DOMAIN_REGEX = /^[a-zA-Z0-9_.+-]+@(octo.com|passculture.app|btmx.fr)/g
const SANDBOX_DOMAIN_REGEX = /^[a-zA-Z0-9_.+-]+@(momarx.io|hlettre.com|youpi.com|violet.fr)/g

const getUserType = email => {
  if (email.match(SANDBOX_DOMAIN_REGEX)) {
    return 'SANDBOX USER on WEBAPP'
  } else if (email.match(TEAM_DOMAIN_REGEX)) {
    return 'TECH or BIZ on WEBAPP'
  } else {
    return 'BENEFICIARY on WEBAPP'
  }
}

const Matomo = ({ location, canBookFreeOffers, email }) => {
  const Matomo = window._paq
  let userId = 'ANONYMOUS'

  const { pathname, search } = location
  const searchParameters = queryString.parse(search)
  const searchKeyword = searchParameters['mots-cles']

  Matomo.push(['setCustomUrl', pathname])
  Matomo.push(['setDocumentTitle', document.title])

  if (searchKeyword) {
    const categories = searchParameters['categories'] || false
    const numberOfResults = false

    Matomo.push(['trackSiteSearch', searchKeyword, categories, numberOfResults])
  }

  if (canBookFreeOffers) {
    userId = 'BENEFICIARY on WEBAPP'
  }

  if (email) {
    userId = getUserType(email)
  }

  Matomo.push(['setUserId', userId])

  if (location.pathname == '/connexion') {
    Matomo.push(['resetUserId'])
  }

  Matomo.push(['trackPageView'])

  return null
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Matomo
