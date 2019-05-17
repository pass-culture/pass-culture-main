import PropTypes from 'prop-types'
import { withRouter } from 'react-router'

const MatomoTracker = ({ location }) => {
  // eslint-disable-next-line
  const matomoTracker = window._paq || []

  matomoTracker.push(['setCustomUrl', location.pathname])
  matomoTracker.push(['setDocumentTitle', document.title])
  matomoTracker.push(['trackPageView'])

  return null
}

MatomoTracker.propTypes = {
  location: PropTypes.shape().isRequired,
}

export default withRouter(MatomoTracker)
