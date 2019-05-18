import PropTypes from 'prop-types'
import { withRouter } from 'react-router'

const MatomoPageTracker = ({ location }) => {
  // eslint-disable-next-line
  const MatomoPageTracker = window._paq || []

  MatomoPageTracker.push(['setCustomUrl', location.pathname])
  MatomoPageTracker.push(['setDocumentTitle', document.title])
  MatomoPageTracker.push(['trackPageView'])

  return null
}

MatomoPageTracker.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default withRouter(MatomoPageTracker)
