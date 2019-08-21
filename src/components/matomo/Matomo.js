import PropTypes from 'prop-types'
import queryString from 'query-string'

const Matomo = ({ location, id, canBookFreeOffers }) => {
  const Matomo = window._paq
  let userId = 'Anonymous'
  let userType = 'Unknown type'

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

  if (id) {
    userId = id
  }
  if (canBookFreeOffers) {
    userType = 'Beneficiary'
  }

  Matomo.push(['setUserId', userId, userType])

  return null
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Matomo
