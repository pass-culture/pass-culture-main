import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './Deck/DeckContainer'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import AbsoluteFooterContainer from '../../layout/AbsoluteFooter/AbsoluteFooterContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import isDetailsView from '../../../helpers/isDetailsView'
import isCancelView from '../../../helpers/isCancelView'
import { MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS } from './utils/utils'

class Discovery extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      atWorldsEnd: false,
      hasError: false,
      isEmpty: null,
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
      updateSeedAndLastRequestTimestamp
    } = this.props
    const { location: prevLocation } = prevProps

    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }

    if (Date.now() > seedLastRequestTimestamp + MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS) {
      updateSeedAndLastRequestTimestamp()
    }
  }

  componentWillUnmount() {
    const { deleteTutorials, tutorials } = this.props

    if (tutorials.length > 0) {
      deleteTutorials(tutorials)
    }
  }

  handleFail = () => {
    const { redirectHome } = this.props

    this.setState(
      { hasError: true, isLoading: true },
      redirectHome
    )
  }

  handleSuccess = (state, action) => {
    const {
      recommendations,
      resetReadRecommendations,
      redirectToFirstRecommendationIfNeeded,
    } = this.props

    const { data: loadedRecommendations = [] } = (action && action.payload)
    const atWorldsEnd = loadedRecommendations.length === 0
    const isEmpty = (!recommendations || !recommendations.length) && atWorldsEnd

    this.setState(
      { atWorldsEnd, isEmpty, isLoading: false },
      () => {
        resetReadRecommendations()
        redirectToFirstRecommendationIfNeeded(loadedRecommendations)
      }
    )
  }

  updateRecommendations = () => {
    const {
      currentRecommendation,
      loadRecommendations,
      page,
      readRecommendations,
      recommendations,
      seed,
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
        page,
        recommendations,
        readRecommendations,
        seed,
        shouldReloadRecommendations
      )
    })
  }

  renderBooking = () => {
    const { currentRecommendation } = this.props
    return (
      <BookingContainer
        recommendation={currentRecommendation}
      />
    )
  }

  renderBookingCancellation = () => (
    <BookingCancellationContainer />
  )

  renderDeck = () => (
    <DeckContainer
      handleRequestPutRecommendations={this.updateRecommendations}
    />
  )

  render() {
    const { match } = this.props
    const { hasError, isEmpty, isLoading } = this.state
    const cancelView = isCancelView(match)

    return (
      <Fragment>
        <main className="discovery-page no-padding page with-footer">
          {!isEmpty && (
            <Fragment>
              <Route
                key="route-discovery-deck"
                path="/decouverte/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?"
                render={this.renderDeck}
              />
              <Route
                key="route-discovery-booking"
                path="/decouverte/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
                render={cancelView
                  ? this.renderBookingCancellation
                  : this.renderBooking}
              />
            </Fragment>
          )}
          <AbsoluteFooterContainer
            areDetailsVisible={isDetailsView(match)}
            borderTop
            id="deck-footer"
          />
        </main>
        <LoaderContainer
          hasError={hasError}
          isEmpty={isEmpty}
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
  currentRecommendation: PropTypes.shape(),
  deleteTutorials: PropTypes.func.isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
    }),
  }).isRequired,
  page: PropTypes.number.isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectHome: PropTypes.func.isRequired,
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  saveLastRecommendationsRequestTimestamp: PropTypes.func.isRequired,
  seed: PropTypes.number.isRequired,
  seedLastRequestTimestamp: PropTypes.number.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  tutorials: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  updateSeedAndLastRequestTimestamp: PropTypes.func.isRequired,
}

export default Discovery
