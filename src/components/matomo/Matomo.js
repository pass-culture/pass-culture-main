import PropTypes from 'prop-types'

const Matomo = ({ location }) => {
  const Matomo = window._paq || []

  Matomo.push(['setCustomUrl', location.pathname])
  Matomo.push(['setDocumentTitle', document.title])

  return null
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default Matomo
