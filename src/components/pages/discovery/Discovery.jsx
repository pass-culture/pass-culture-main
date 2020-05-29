import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './Deck/DeckContainer'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import isCancelView from '../../../utils/isCancelView'
import { MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS } from './utils/utils'

class Discovery extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      atWorldsEnd: false,
      hasError: false,
      hasError500: false,
      hasNoMoreRecommendations: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const {
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      saveLastRecommendationsRequestTimestamp,
      shouldReloadRecommendations,
    } = this.props

    if (shouldReloadRecommendations) {
      this.updateRecommendations()
      saveLastRecommendationsRequestTimestamp()
    } else {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }
  }

  componentDidUpdate(prevProps) {
    const {
      location,
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      seedLastRequestTimestamp,
      updateLastRequestTimestamp,
    } = this.props
    const { location: prevLocation } = prevProps

    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }

    if (Date.now() > seedLastRequestTimestamp + MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS) {
      updateLastRequestTimestamp()
    }
  }

  handleFail = (state, action) => {
    this.setState({
      hasError: true,
      hasError500: action.payload.status === 500 ? true : false,
      hasNoMoreRecommendations: true,
      isLoading: false,
    })
  }

  handleSuccess = (state, action) => {
    const {
      recommendations,
      resetReadRecommendations,
      redirectToFirstRecommendationIfNeeded,
    } = this.props

    const { data: loadedRecommendations = [] } = action && action.payload
    const atWorldsEnd = loadedRecommendations.length === 0
    const hasNoMoreRecommendations = (!recommendations || !recommendations.length) && atWorldsEnd

    this.setState({ atWorldsEnd, hasNoMoreRecommendations, isLoading: false }, () => {
      resetReadRecommendations()
      redirectToFirstRecommendationIfNeeded(loadedRecommendations)
    })
  }

  updateRecommendations = () => {
    const {
      currentRecommendation,
      loadRecommendations,
      readRecommendations,
      recommendations,
      shouldReloadRecommendations,
    } = this.props

    const { atWorldsEnd, isLoading } = this.state
    if (atWorldsEnd || isLoading) {
      return
    }

    this.setState({ isLoading: true }, () => {
      loadRecommendations(
        this.handleSuccess,
        this.handleFail,
        currentRecommendation,
        recommendations,
        readRecommendations,
        shouldReloadRecommendations
      )
    })
  }

  renderBooking = () => {
    const { currentRecommendation } = this.props
    return <BookingContainer recommendation={currentRecommendation} />
  }

  renderBookingCancellation = () => <BookingCancellationContainer />

  renderDeck = () => <DeckContainer handleRequestPutRecommendations={this.updateRecommendations} />

  render() {
    const { match } = this.props
    const { hasError, hasError500, hasNoMoreRecommendations, isLoading } = this.state
    const cancelView = isCancelView(match)

    return (
      <Fragment>
        {!hasNoMoreRecommendations && !isLoading && (
          <main className="discovery-page no-padding page">
            <Route
              key="route-discovery-deck"
              path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?"
              render={this.renderDeck}
              sensitive
            />
            <Route
              key="route-discovery-booking"
              path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
              render={cancelView ? this.renderBookingCancellation : this.renderBooking}
              sensitive
            />
          </main>
        )}
        {isLoading && (
          <LoaderContainer
            hasError={hasError}
            hasError500={hasError500}
            hasNoMoreRecommendations={hasNoMoreRecommendations}
            isLoading={isLoading}
          />
        )}
      </Fragment>
    )
  }
}

Discovery.defaultProps = {
  currentRecommendation: null,
  readRecommendations: null,
  recommendations: null,
}

Discovery.propTypes = {
  currentRecommendation: PropTypes.shape(),
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
    }),
  }).isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  saveLastRecommendationsRequestTimestamp: PropTypes.func.isRequired,
  seedLastRequestTimestamp: PropTypes.number.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  updateLastRequestTimestamp: PropTypes.func.isRequired,
}

export default Discovery
