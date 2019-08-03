import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../Booking/BookingContainer'
import RectoContainer from '../Recto/RectoContainer'
import VersoContainer from '../Verso/VersoContainer'
import getAreDetailsVisible from '../../../helpers/getAreDetailsVisible'
import getIsTransitionDetailsUrl from '../../../helpers/getIsTransitionDetailsUrl'

class Details extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      forceDetailsVisible: false
    }
  }

  componentDidMount() {
    const { hasReceivedData, needsToRequestGetData, requestGetData } = this.props

    if (hasReceivedData) {
      this.handleSetForceDetailsVisible(true)
      return
    }

    if (!needsToRequestGetData) {
      return
    }

    requestGetData(this.handleSetForceDetailsVisible)
  }

  componentDidUpdate (prevProps) {
    const { hasReceivedData, match } = this.props
    const { forceDetailsVisible } = this.state

    const hasJustReceivedData = !forceDetailsVisible &&
      hasReceivedData &&
      !prevProps.hasReceivedData
    const areDetailsVisible = getAreDetailsVisible(match)
    const previousAreDetailsVisible = getAreDetailsVisible(prevProps.match)
    const hasDetailsVisibleJustHappened = areDetailsVisible
      && !previousAreDetailsVisible
    if (hasJustReceivedData || hasDetailsVisibleJustHappened) {
      this.handleSetForceDetailsVisible(true)
      return
    }

    const hasTransitionJustHappened = getIsTransitionDetailsUrl(match)
      && !getIsTransitionDetailsUrl(prevProps.match)
    const hasRemovedDetailsJustHappened = !areDetailsVisible
      && previousAreDetailsVisible
    if (hasTransitionJustHappened || hasRemovedDetailsJustHappened) {
      this.handleSetForceDetailsVisible(false)
    }

  }

  handleSetForceDetailsVisible = forceDetailsVisible => {
    this.setState({ forceDetailsVisible })
  }

  renderBooking = route => {
    return (
      <BookingContainer
        extraClassName="with-header"
        {...route}
      />
    )
  }

  render() {
    const { bookingPath, forceDetailsVisible } = this.state

    return (
      <Fragment>
        {forceDetailsVisible && (
          <Route
            path={bookingPath}
            render={this.renderBooking}
          />
        )}
        <VersoContainer
          areDetailsVisible={forceDetailsVisible}
          extraClassName="with-header"
        />
        {forceDetailsVisible && (
          <RectoContainer
            areDetailsVisible
            extraClassName="with-header"
          />)}
      </Fragment>
    )
  }
}

Details.propTypes = {
  hasReceivedData: PropTypes.bool.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
    search: PropTypes.string
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string
    }).isRequired
  }).isRequired,
  needsToRequestGetData: PropTypes.bool.isRequired,
  requestGetData: PropTypes.func.isRequired
}

export default Details
