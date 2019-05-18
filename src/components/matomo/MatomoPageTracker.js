import PropTypes from 'prop-types'
import { withRouter } from 'react-router'

const MatomoPageTracker = ({ location }) => {
  const MatomoTracker = window._paq || []

  MatomoTracker.push(['setCustomUrl', location.pathname])
  MatomoTracker.push(['setDocumentTitle', document.title])
  MatomoTracker.push(['trackPageView'])

  return null
}

MatomoPageTracker.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default withRouter(MatomoPageTracker)
