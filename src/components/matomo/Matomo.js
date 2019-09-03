import PropTypes from 'prop-types'

const Matomo = ({ location, userId }) => {
  const Matomo = window._paq || []
  Matomo.push(['setCustomUrl', location.pathname])
  Matomo.push(['setDocumentTitle', document.title])

  Matomo.push(['setUserId', userId + ' on PRO'])

  if (location.pathname == '/connexion') {
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
