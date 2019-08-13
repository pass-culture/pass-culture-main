import PropTypes from 'prop-types'
import queryString from 'query-string'

const Matomo = ({ location }) => {
  const Matomo = window._paq
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

  return null
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Matomo
