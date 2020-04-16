import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './Deck/DeckContainer'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import AbsoluteFooterContainer from '../../layout/AbsoluteFooter/AbsoluteFooterContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import isDetailsView from '../../../utils/isDetailsView'
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
      history,
      location,
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      match,
      seedLastRequestTimestamp,
      updateLastRequestTimestamp,
    } = this.props
    const { location: prevLocation, recommendations: prevRecommendations } = prevProps

    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte-v3') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }

    if (Date.now() > seedLastRequestTimestamp + MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS) {
      updateLastRequestTimestamp()
    }

    if (prevRecommendations !== recommendations) {
      const { params } = match
      const { offerId } = params
      const isOfferInReco = recommendations.filter(reco => reco.offerId === offerId).length > 0
      if (recommendations.length > 0 && !isOfferInReco) {
        history.push('/decouverte-v3')
      }
    }
  }

  componentWillUnmount() {
    const { resetRecommendations } = this.props
    resetRecommendations()
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
      coordinates,
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
        shouldReloadRecommendations,
        coordinates
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
    const { hasError, hasNoMoreRecommendations, isLoading, hasError500 } = this.state
    const cancelView = isCancelView(match)

    return (
      <Fragment>
        {!hasNoMoreRecommendations && (
          <main className="discovery-page no-padding page with-footer">
            <Route
              key="route-discovery-deck"
              path="/decouverte-v3/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?"
              render={this.renderDeck}
              sensitive
            />
            <Route
              key="route-discovery-booking"
              path="/decouverte-v3/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
              render={cancelView ? this.renderBookingCancellation : this.renderBooking}
              sensitive
            />
            <AbsoluteFooterContainer
              areDetailsVisible={isDetailsView(match)}
              borderTop
              id="deck-footer"
            />
          </main>
        )}
        <LoaderContainer
          hasError={hasError}
          hasError500={hasError500}
          hasNoMoreRecommendations={hasNoMoreRecommendations}
          isLoading={isLoading}
        />
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
  coordinates: PropTypes.shape().isRequired,
  currentRecommendation: PropTypes.shape(),
  history: PropTypes.shape().isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
      offerId: PropTypes.string,
    }),
  }).isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  resetRecommendations: PropTypes.func.isRequired,
  saveLastRecommendationsRequestTimestamp: PropTypes.func.isRequired,
  seedLastRequestTimestamp: PropTypes.number.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  updateLastRequestTimestamp: PropTypes.func.isRequired,
}

export default Discovery
