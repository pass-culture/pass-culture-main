import PropTypes from 'prop-types'
import { withRouter } from 'react-router'
import { Component } from 'react'

export class MatomoTracker extends Component {
  render() {
    const { children, location } = this.props

    // eslint-disable-next-line
    const matomoTracker = window._paq || []

    if (location) {
      matomoTracker.push(['setCustomUrl', location.pathname])
      matomoTracker.push(['setDocumentTitle', document.title])
      matomoTracker.push(['trackPageView'])
    }

    return children
  }
}

MatomoTracker.propTypes = {
  children: PropTypes.node.isRequired,
  location: PropTypes.shape(),
}

MatomoTracker.defaultProps = {
  location: null,
}

export default withRouter(MatomoTracker)
