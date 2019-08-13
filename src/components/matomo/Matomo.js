import PropTypes from 'prop-types'
import { withRouter } from 'react-router'

const Matomo = ({ location }) => {
  const Matomo = window._paq || []

  Matomo.push(['setCustomUrl', location.pathname])
  Matomo.push(['setDocumentTitle', document.title])
  Matomo.push(['trackPageView'])

  return null
}

Matomo.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default withRouter(Matomo)
